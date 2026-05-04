"""
NEPSE Weekly Buy Streamlit UI

Features:
- Weekly buy suggestion button
- Editable bought price and quantity for suggested shares
- Save positions in a database for persistence
- Start/stop an auto bot that resumes from saved positions
"""
from __future__ import annotations

import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from src.bot.market_analyzer import MarketAnalyzer
from src.bot.market_history import WeeklyMarketHistory
from src.bot.portfolio_bot import PortfolioBotManager
from src.bot.position_store import build_position_record, list_positions, load_position, save_position, delete_position, migrate_positions
from src.bot.trade_history import get_trade_history, get_trade_statistics, get_trades_by_symbol, delete_trade
from src.bot.notification import send_email_notification

# Try to import legacy trade migration (available in newer versions)
try:
    from src.bot.trade_history import migrate_legacy_trades
except ImportError:
    migrate_legacy_trades = None


ENV_FILE = ".env"


def is_market_open() -> bool:
    """Check if NEPSE is open based on Nepal time (Monday to Friday)."""
    timezone_name = load_env_value("MARKET_TIMEZONE", "Asia/Kathmandu")
    try:
        now = datetime.now(ZoneInfo(timezone_name))
    except Exception:
        now = datetime.now(ZoneInfo("Asia/Kathmandu"))

    weekday = now.weekday()  # 0=Monday, 6=Sunday
    hour = now.hour
    
    # Market is closed on weekends
    if weekday >= 5:  # Saturday or Sunday
        return False
    
    open_hour = load_env_int("MARKET_OPEN_HOUR", 9)
    close_hour = load_env_int("MARKET_CLOSE_HOUR", 15)
    return open_hour <= hour < close_hour


def load_env_value(key: str, default: str = "") -> str:
    """Load an env value from the current process or .env file."""
    value = os.getenv(key)
    if value:
        return value

    if not os.path.exists(ENV_FILE):
        return default

    try:
        with open(ENV_FILE, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == key:
                    return v.strip().strip('"').strip("'")
    except OSError:
        pass

    return default


def load_env_int(key: str, default: int) -> int:
    """Load an integer env value with fallback."""
    value = load_env_value(key, str(default))
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_positions_db_path() -> str:
    """Return configured SQLite path for saved positions."""
    return load_env_value("POSITIONS_DB_PATH", load_env_value("POSITIONS_DIR", "data/positions.db"))


def ensure_positions_migrated() -> None:
    """Migrate legacy JSON position files into the configured SQLite database."""
    migrate_positions(source_dirs=["logs", "data/positions"], target_dir=get_positions_db_path())


def check_storage_health() -> None:
    """Display which storage target is active and whether it can be queried."""
    try:
        target = get_positions_db_path()
        try:
            positions = list_positions(target)
            count = len(positions)
            st.sidebar.success(f"Storage: SQLite ({target}) — {count} positions")
        except Exception as e:
            st.sidebar.error(f"Storage connection error: {str(e)}")
    except Exception:
        # Fail silently if position_store import isn't available for some reason
        pass


def save_env_values(values: dict[str, str], env_file: str = ENV_FILE) -> None:
    """Update or append key/value pairs in .env."""
    existing_lines = []
    existing_keys = set()

    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as file:
                existing_lines = file.readlines()
        except OSError:
            existing_lines = []

    updated_lines = []
    for raw_line in existing_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            updated_lines.append(raw_line)
            continue

        key = stripped.split("=", 1)[0].strip()
        if key in values:
            updated_lines.append(f"{key}={values[key]}\n")
            existing_keys.add(key)
        else:
            updated_lines.append(raw_line)

    for key, value in values.items():
        if key not in existing_keys:
            updated_lines.append(f"{key}={value}\n")

    with open(env_file, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

    for key, value in values.items():
        os.environ[key] = value


st.set_page_config(
    page_title="NEPSE Weekly Buy Bot",
    page_icon="📈",
    layout="wide",
)

st.title("NEPSE Weekly Buy Bot")
st.caption("Suggest weekly purchases, save bought price and quantity, and run an auto bot from SQLite-saved positions.")

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
if "suggestions_df" not in st.session_state:
    st.session_state.suggestions_df = None
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "bot_manager" not in st.session_state:
    st.session_state.bot_manager = None
if "bot_started_at" not in st.session_state:
    st.session_state.bot_started_at = None
if "bot_stopped_at" not in st.session_state:
    st.session_state.bot_stopped_at = None
if "bot_auto_disabled" not in st.session_state:
    st.session_state.bot_auto_disabled = False
if "auto_bot_checked" not in st.session_state:
    st.session_state.auto_bot_checked = False
if "position_added" not in st.session_state:
    st.session_state.position_added = False
if "last_added_position" not in st.session_state:
    st.session_state.last_added_position = None

# -----------------------------------------------------------------------------
# Sidebar settings
# -----------------------------------------------------------------------------
st.sidebar.header("Settings")
capital_per_stock = st.sidebar.number_input(
    "Capital per stock (Rs.)",
    min_value=1000.0,
    value=10000.0,
    step=500.0,
)
min_volume = st.sidebar.number_input(
    "Minimum volume filter",
    min_value=0,
    value=50000,
    step=1000,
)
max_suggestions = st.sidebar.selectbox("Suggested shares", [5], index=0)
bot_interval_seconds = st.sidebar.number_input(
    "Auto bot check interval (seconds)",
    min_value=30,
    value=load_env_int("BOT_CHECK_INTERVAL_SECONDS", 30),
    step=30,
)

st.sidebar.info("The bot uses saved entry price and quantity from the SQLite positions database.")

ensure_positions_migrated()
if migrate_legacy_trades:
    migrate_legacy_trades()

st.sidebar.markdown("---")
st.sidebar.subheader("Email Alerts")
if st.sidebar.button("Send Test Email", use_container_width=True):
    try:
        sent = send_email_notification(
            subject="NEPSE Bot Test Email",
            body="This is a test email from NEPSE Weekly Buy Bot. If you received this, Gmail setup is working.",
        )
        if sent:
            st.sidebar.success("Test email sent successfully")
        else:
            st.sidebar.error("Test email failed. Check EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, and EMAIL_TO environment variables.")
    except Exception as e:
        st.sidebar.error(f"Test email failed: {str(e)}")

history_store = WeeklyMarketHistory()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def build_suggestion_dataframe(suggestions):
    rows = []
    for symbol, data, score in suggestions:
        price = float(data["ltp"])
        quantity = max(1, int(capital_per_stock / price))
        rows.append(
            {
                "symbol": symbol,
                "ltp": round(price, 2),
                "volume": int(data.get("volume", 0)),
                "pct_change": round(float(data.get("pct_change", 0.0)), 2),
                "score": round(float(score), 3),
                "days_observed": int(data.get("days_observed", 1)),
                "avg_volume": int(data.get("avg_volume", data.get("volume", 0))),
                "avg_pct_change": round(float(data.get("avg_pct_change", data.get("pct_change", 0.0))), 2),
                "consistency": round(float(data.get("consistency", 1.0)), 2),
                "trend_delta": round(float(data.get("trend_delta", 0.0)), 2),
                "bought_price": round(price, 2),
                "quantity": quantity,
                "total_invested": round(quantity * price, 2),
            }
        )
    return pd.DataFrame(rows)


def refresh_positions_df():
    positions = list_positions(get_positions_db_path())
    if not positions:
        return pd.DataFrame(columns=["symbol", "shares", "avg_cost", "total_invested", "cash", "current_price", "entry_price", "stop_loss", "saved_at"])

    rows = []
    for pos in positions:
        rows.append(
            {
                "symbol": pos.get("symbol"),
                "shares": pos.get("shares"),
                "avg_cost": pos.get("avg_cost"),
                "total_invested": pos.get("total_invested"),
                "cash": pos.get("cash"),
                "current_price": pos.get("current_price"),
                "entry_price": pos.get("entry_price"),
                "stop_loss": pos.get("stop_loss"),
                "saved_at": pos.get("saved_at"),
                "file_path": pos.get("file_path"),
            }
        )
    return pd.DataFrame(rows)


def ensure_bot_manager():
    manager = st.session_state.bot_manager
    if manager is None:
        manager = PortfolioBotManager(positions_db_path=get_positions_db_path(), check_interval_seconds=int(bot_interval_seconds))
        st.session_state.bot_manager = manager
    return manager


def start_auto_bot(manager: PortfolioBotManager, force_reload: bool = True) -> bool:
    """Start the background auto bot if saved positions exist."""
    manager.check_interval_seconds = int(bot_interval_seconds)
    manager.positions_db_path = get_positions_db_path()
    manager.load_traders(force=force_reload)
    if not manager.traders:
        return False

    manager.start_background()
    st.session_state.bot_started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.bot_stopped_at = None
    st.session_state.bot_auto_disabled = False
    return True


def stop_auto_bot(manager: PortfolioBotManager, suppress_save: bool = False) -> None:
    """Stop the background auto bot and remember the manual stop.

    If `suppress_save` is True, the manager will not persist trader positions
    when shutting down (used during delete to avoid recreating files).
    """
    try:
        manager.stop(suppress_save=suppress_save)
    except TypeError:
        # Fallback for older manager.stop() signatures
        manager.stop()

    st.session_state.bot_stopped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.bot_auto_disabled = True


def sync_market_hours_bot() -> None:
    """Auto-start the bot during market hours unless the user stopped it manually."""
    manager = ensure_bot_manager()
    manager.check_interval_seconds = int(bot_interval_seconds)
    manager.positions_db_path = get_positions_db_path()

    if not is_market_open():
        st.session_state.bot_auto_disabled = False
        return

    if st.session_state.bot_auto_disabled or manager.running:
        return

    if list_positions(get_positions_db_path()) and start_auto_bot(manager, force_reload=True):
        st.info(f"🚀 Auto bot started during market hours ({len(manager.traders)} position(s))")


sync_market_hours_bot()


# -----------------------------------------------------------------------------
# Main actions
# -----------------------------------------------------------------------------
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Weekly Buy Suggest", type="primary", use_container_width=True):
        analyzer = MarketAnalyzer()
        with st.spinner("Fetching live market data from ShareSansar..."):
            all_stocks = analyzer.fetch_all_stocks_data(source="sharesansar")

        if not all_stocks:
            st.error("Failed to fetch market data.")
        else:
            snapshots = history_store.add_snapshot(all_stocks)
            suggestions = history_store.get_weekly_top_stocks(
                current_snapshot=all_stocks,
                top_n=max_suggestions,
                min_volume=int(min_volume),
                min_momentum=0.0,
            )
            st.session_state.last_analysis = {
                "fetched": len(all_stocks),
                "suggested": len(suggestions),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "history_days": len(snapshots),
            }
            st.session_state.suggestions_df = build_suggestion_dataframe(suggestions)

with col2:
    st.metric("Saved positions", len(list_positions(get_positions_db_path())))

if st.session_state.last_analysis:
    info = st.session_state.last_analysis
    st.success(
        f"Fetched {info['fetched']} stocks | Suggested {info['suggested']} stock(s) | {info['time']}"
    )
    st.caption(f"Historical days stored: {info.get('history_days', 0)}/7")

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab_suggest, tab_positions, tab_bot, tab_history = st.tabs(["Weekly Suggestion", "Saved Positions", "Auto Bot", "Trade History"])

with tab_suggest:
    st.subheader("Weekly buy suggestion")
    st.write("Use the button above to fetch live market data, store it in the 7-day history, and suggest the top 5 shares.")

    if st.session_state.suggestions_df is None or st.session_state.suggestions_df.empty:
        st.info("No suggestions loaded yet. Click **Weekly Buy Suggest** first.")
    else:
        st.markdown("### Edit bought price and quantity")
        edited_df = st.data_editor(
            st.session_state.suggestions_df,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            disabled=["symbol", "ltp", "volume", "pct_change", "score", "days_observed", "avg_volume", "avg_pct_change", "consistency", "trend_delta", "total_invested"],
            column_config={
                "symbol": st.column_config.TextColumn("Symbol"),
                "ltp": st.column_config.NumberColumn("LTP", format="%.2f"),
                "volume": st.column_config.NumberColumn("Volume"),
                "pct_change": st.column_config.NumberColumn("% Change", format="%.2f"),
                "score": st.column_config.NumberColumn("Score", format="%.3f"),
                "days_observed": st.column_config.NumberColumn("Days", format="%d"),
                "avg_volume": st.column_config.NumberColumn("Avg Volume"),
                "avg_pct_change": st.column_config.NumberColumn("Avg % Change", format="%.2f"),
                "consistency": st.column_config.NumberColumn("Consistency", format="%.2f"),
                "trend_delta": st.column_config.NumberColumn("Trend Δ", format="%.2f"),
                "bought_price": st.column_config.NumberColumn("Bought Price", min_value=0.0, step=0.05),
                "quantity": st.column_config.NumberColumn("Quantity", min_value=1, step=1),
                "total_invested": st.column_config.NumberColumn("Total Invested"),
            },
        )

        if st.button("Save Bought Positions", use_container_width=True):
            saved_files = []
            for _, row in edited_df.iterrows():
                symbol = str(row["symbol"]).upper()
                bought_price = float(row["bought_price"])
                quantity = int(row["quantity"])
                if quantity <= 0 or bought_price <= 0:
                    continue

                position = build_position_record(
                    symbol=symbol,
                    shares=quantity,
                    avg_cost=bought_price,
                    total_invested=quantity * bought_price,
                    cash=1000000,
                    current_price=bought_price,
                    entry_price=bought_price,
                    source="streamlit",
                    bought_via="weekly_suggestion",
                )
                saved_path = save_position(position, positions_dir=get_positions_db_path())
                saved_files.append(saved_path)

            if saved_files:
                st.success(f"Saved {len(saved_files)} position(s) in SQLite:")
                for path in saved_files:
                    st.write(path)
            else:
                st.warning("No valid rows were saved.")

with tab_positions:
    st.subheader("Saved positions")

    manager = ensure_bot_manager()
    manager.check_interval_seconds = int(bot_interval_seconds)
    manager.positions_db_path = get_positions_db_path()

    bot_status_col1, bot_status_col2, bot_status_col3, bot_status_col4 = st.columns(4)
    with bot_status_col1:
        st.metric("Bot status", "Running" if manager.running else "Stopped")
    with bot_status_col2:
        st.metric("Market open", "Yes" if is_market_open() else "No")
    with bot_status_col3:
        st.metric("Loaded traders", len(manager.traders))
    with bot_status_col4:
        st.metric("Check interval", f"{int(bot_interval_seconds)}s")

    toggle_label = "Stop Auto Bot" if manager.running else "Start Auto Bot"
    toggle_type = "secondary" if manager.running else "primary"
    if st.button(toggle_label, type=toggle_type, use_container_width=True, key="positions_bot_toggle"):
        if manager.running:
            stop_auto_bot(manager)
            st.success("Auto bot stopped.")
        else:
            if start_auto_bot(manager, force_reload=True):
                st.success("Auto bot started in background.")
            else:
                st.warning("No saved positions found. Save a position first.")
        st.rerun()

    if st.session_state.bot_started_at:
        st.info(f"Bot started at: {st.session_state.bot_started_at}")
    if st.session_state.bot_stopped_at:
        st.caption(f"Bot stopped at: {st.session_state.bot_stopped_at}")

    st.warning("If the bot is running, update or delete actions will pause it briefly and restart it after the change.")
    
    st.markdown("### Add Manual Position")
    col_add1, col_add2, col_add3 = st.columns(3)
    with col_add1:
        new_symbol = st.text_input("Symbol", placeholder="e.g., PCBLP", key="manual_symbol").upper()
    with col_add2:
        new_shares = st.number_input("Shares", min_value=1, value=1, step=1, key="manual_shares")
    with col_add3:
        new_price = st.number_input("Bought Price (Rs.)", min_value=0.01, value=100.0, step=0.05, key="manual_price")
    
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        if st.button("Add Position", use_container_width=True, type="primary"):
            if not new_symbol or new_shares <= 0 or new_price <= 0:
                st.error("❌ Please fill all fields with valid values.")
            else:
                try:
                    position = build_position_record(
                        symbol=new_symbol,
                        shares=int(new_shares),
                        avg_cost=float(new_price),
                        total_invested=int(new_shares) * float(new_price),
                        cash=1000000,
                        current_price=float(new_price),
                        entry_price=float(new_price),
                        source="streamlit_manual",
                    )
                    saved_path = save_position(position, positions_dir=get_positions_db_path())
                    st.session_state.position_added = True
                    st.session_state.last_added_position = new_symbol
                    with st.empty():
                        st.success(f"✓ Position saved: {new_symbol}")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving position: {str(e)}")
    
    # Show feedback if position was just added
    if st.session_state.get("position_added", False):
        st.session_state.position_added = False
    
    st.divider()
    positions_df = refresh_positions_df()
    
    col_view1, col_view2 = st.columns([4, 1])
    with col_view1:
        st.markdown("### View & Edit")
    with col_view2:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_positions"):
            positions_df = refresh_positions_df()
            st.rerun()
    
    st.dataframe(positions_df, use_container_width=True, hide_index=True)

    if not positions_df.empty:
        st.markdown("### Edit Position")
        symbol_options = positions_df["symbol"].dropna().astype(str).tolist()
        selected_symbol = st.selectbox("Select position to edit", symbol_options, key="edit_selector")
        preview = load_position(selected_symbol, positions_dir=get_positions_db_path())
        if preview:
            st.markdown(f"**{selected_symbol} Position**")

            col_e1, col_e2, col_e3, col_e4 = st.columns(4)
            with col_e1:
                edit_shares = st.number_input(
                    "Shares",
                    min_value=1,
                    value=int(preview.get("shares", 1)),
                    step=1,
                    key=f"edit_shares_{selected_symbol}",
                )
            with col_e2:
                edit_price = st.number_input(
                    "Bought Price (Rs.)",
                    min_value=0.01,
                    value=float(preview.get("avg_cost", 100)),
                    step=0.05,
                    key=f"edit_price_{selected_symbol}",
                )
            with col_e3:
                edit_current = st.number_input(
                    "Current Price (Rs.)",
                    min_value=0.01,
                    value=float(preview.get("current_price", 100)),
                    step=0.05,
                    key=f"edit_current_{selected_symbol}",
                )
            with col_e4:
                edit_stop_loss = st.number_input(
                    "Stop Loss (Rs.)",
                    min_value=0.01,
                    value=float(preview.get("stop_loss", preview.get("avg_cost", 100) * 0.9)),
                    step=0.05,
                    key=f"edit_stop_loss_{selected_symbol}",
                )

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                update_clicked = st.button(
                    "Update Position",
                    type="primary",
                    use_container_width=True,
                    key=f"update_position_{selected_symbol}",
                )
            with btn_col2:
                st.button("View JSON", disabled=True, use_container_width=True, key=f"view_json_{selected_symbol}")

            if update_clicked:
                bot_was_running = bool(manager.running)
                if bot_was_running:
                    stop_auto_bot(manager)

                updated_position = build_position_record(
                    symbol=selected_symbol,
                    shares=int(edit_shares),
                    avg_cost=float(edit_price),
                    total_invested=int(edit_shares) * float(edit_price),
                    cash=float(preview.get("cash", 1000000)),
                    current_price=float(edit_current),
                    entry_price=float(edit_price),
                    stop_loss=float(edit_stop_loss),
                )
                save_position(updated_position, positions_dir=get_positions_db_path())

                if bot_was_running and is_market_open():
                    start_auto_bot(manager, force_reload=True)

                st.success(f"✓ Position updated: {selected_symbol}")
                st.rerun()

            if st.button("Delete Position", type="secondary", use_container_width=True, key=f"delete_position_{selected_symbol}"):
                bot_was_running = bool(manager.running)
                if bot_was_running:
                    stop_auto_bot(manager, suppress_save=True)

                delete_position(selected_symbol, positions_dir=get_positions_db_path())
                
                # Remove the trader from memory to prevent it from writing files after deletion
                if selected_symbol in manager.traders:
                    del manager.traders[selected_symbol]

                if bot_was_running and is_market_open():
                    start_auto_bot(manager, force_reload=True)

                st.success(f"✓ Position deleted: {selected_symbol}")
                st.rerun()

            st.json(preview)

with tab_bot:
    st.subheader("Auto bot")
    st.write(
        "The auto bot loads saved positions from SQLite, uses the stored bought price as the entry reference, "
        "and monitors price changes similar to the GUFL bot."
    )

    manager = ensure_bot_manager()
    manager.check_interval_seconds = int(bot_interval_seconds)

    bot_status_col1, bot_status_col2 = st.columns(2)
    with bot_status_col1:
        st.metric("Bot status", "Running" if manager.running else "Stopped")
    with bot_status_col2:
        st.metric("Loaded traders", len(manager.traders))

    btn_toggle, btn_reload = st.columns(2)
    with btn_toggle:
        toggle_label = "Stop Auto Bot" if manager.running else "Start Auto Bot"
        toggle_type = "secondary" if manager.running else "primary"
        if st.button(toggle_label, type=toggle_type, use_container_width=True, key="bot_tab_toggle"):
            if manager.running:
                stop_auto_bot(manager)
                st.success("Auto bot stopped.")
            else:
                if start_auto_bot(manager, force_reload=True):
                    st.success("Auto bot started in background.")
                else:
                    st.warning("No saved positions found. Save a position first.")
            st.rerun()

    with btn_reload:
        if st.button("Reload Positions", use_container_width=True):
            manager.load_traders(force=True)
            st.info("Reloaded positions from the database.")

    if st.session_state.bot_started_at:
        st.info(f"Bot started at: {st.session_state.bot_started_at}")

    if manager.traders:
        status_df = pd.DataFrame(manager.get_status())
        desired_columns = [
            "symbol",
            "position",
            "bought_price",
            "current_price",
            "profit_loss",
            "checks",
            "trades",
            "running",
        ]
        existing_columns = [col for col in desired_columns if col in status_df.columns]
        status_df = status_df[existing_columns]
        st.dataframe(status_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No active traders loaded. Save positions first, then start the bot.")

    st.markdown("### Notes")
    st.markdown(
        "- Each saved symbol is persisted in the SQLite positions database.\n"
        "- The saved `avg_cost` is treated as the initial reference price.\n"
        "- The bot reads this saved position record when resuming the position.\n"
        "- Weekly suggestions use up to 7 saved market snapshots for better selection."
    )

with tab_history:
    st.subheader("Trade History")
    st.write("Complete record of all stocks that have been sold, including profit/loss details.")
    
    # Get trade statistics
    stats = get_trade_statistics()
    
    if stats["total_trades"] > 0:
        # Display statistics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Trades", stats["total_trades"])
        with col2:
            st.metric("Total P&L", f"Rs. {stats['total_pnl']:,.2f}", 
                     delta=f"{stats['avg_pnl_pct']:+.2f}%")
        with col3:
            st.metric("Win Rate", f"{stats['win_rate']:.1f}%")
        with col4:
            st.metric("Shares Sold", stats["total_quantity_sold"])
        
        st.divider()
        
        # Get all trades
        trades = get_trade_history()
        
        # Create display dataframe
        trades_display = []
        for trade in trades:
            trades_display.append({
                "Symbol": trade["symbol"],
                "Quantity": trade["quantity"],
                "Buy Price": f"Rs. {trade['buy_price']:.2f}",
                "Sell Price": f"Rs. {trade['sell_price']:.2f}",
                "Invested": f"Rs. {trade['total_invested']:,.2f}",
                "Proceeds": f"Rs. {trade['total_proceeds']:,.2f}",
                "P&L": f"Rs. {trade['pnl']:,.2f}",
                "P&L %": f"{trade['pnl_pct']:+.2f}%",
                "Sold At": trade["sold_at"],
            })
        
        trades_df = pd.DataFrame(trades_display)
        st.dataframe(trades_df, use_container_width=True, hide_index=True)
        
        # Get all unique symbols
        all_symbols = list(set(trade["symbol"] for trade in trades))
        
        # Delete trades section
        st.markdown("### Delete Trades")
        del_col1, del_col2 = st.columns(2)
        with del_col1:
            selected_del_sym = st.selectbox("Delete all trades for a symbol", 
                                           ["Select symbol..."] + sorted(all_symbols), 
                                           key="delete_symbol_filter")
            if selected_del_sym != "Select symbol...":
                sym_trades_to_delete = get_trades_by_symbol(selected_del_sym)
                if st.button(f"Delete all {selected_del_sym} trades ({len(sym_trades_to_delete)} trades)", 
                            key=f"delete_all_{selected_del_sym}",
                            help=f"Permanently delete all {len(sym_trades_to_delete)} trades for {selected_del_sym}"):
                    deleted_count = 0
                    for trade in sym_trades_to_delete:
                        if delete_trade(trade.get('id'), logs_dir=None):
                            deleted_count += 1
                    st.success(f"✅ Deleted {deleted_count} trades for {selected_del_sym}")
                    st.rerun()
        
        with del_col2:
            if st.button("🗑️ Clear All Trades", key="clear_all_trades", help="Permanently delete all trade history"):
                from src.bot.trade_history import clear_trade_history
                if clear_trade_history(logs_dir=None):
                    st.success("✅ All trade history cleared")
                    st.rerun()
                else:
                    st.error("❌ Failed to clear trade history")
        
        # Filter by symbol
        st.markdown("### Filter by Symbol")
        selected_sym = st.selectbox("Select symbol to view trades", ["All Symbols"] + sorted(all_symbols), key="history_symbol_filter")
        
        if selected_sym != "All Symbols":
            symbol_trades = get_trades_by_symbol(selected_sym)
            if symbol_trades:
                st.markdown(f"#### {selected_sym} Trade History")
                
                sym_display = []
                for idx, trade in enumerate(symbol_trades):
                    sym_display.append({
                        "Trade #": idx + 1,
                        "Buy Price": f"Rs. {trade['buy_price']:.2f}",
                        "Sell Price": f"Rs. {trade['sell_price']:.2f}",
                        "Quantity": trade["quantity"],
                        "P&L": f"Rs. {trade['pnl']:,.2f}",
                        "P&L %": f"{trade['pnl_pct']:+.2f}%",
                        "Sold At": trade["sold_at"],
                    })
                
                sym_df = pd.DataFrame(sym_display)
                st.dataframe(sym_df, use_container_width=True, hide_index=True)
                
                # Select trade to view details and logs
                st.markdown(f"### View Trade Details")
                trade_idx = st.selectbox(f"Select {selected_sym} trade to view details", 
                                        range(len(symbol_trades)), 
                                        format_func=lambda i: f"Trade {i+1} - {symbol_trades[i]['sold_at']}",
                                        key=f"view_trade_{selected_sym}")
                
                if trade_idx is not None:
                    selected_trade = symbol_trades[trade_idx]
                    
                    # Display trade details
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Buy Price", f"Rs. {selected_trade['buy_price']:.2f}")
                    with col2:
                        st.metric("Sell Price", f"Rs. {selected_trade['sell_price']:.2f}")
                    with col3:
                        st.metric("Quantity", selected_trade['quantity'])
                    with col4:
                        pnl_color = "green" if selected_trade['pnl'] >= 0 else "red"
                        st.metric("P&L", f"Rs. {selected_trade['pnl']:,.2f}", 
                                 delta=f"{selected_trade['pnl_pct']:+.2f}%")
                    
                    # Delete trade option
                    st.divider()
                    dcol1, dcol2 = st.columns([3, 1])
                    with dcol2:
                        if st.button("🗑️ Delete Trade", key=f"delete_trade_{selected_trade.get('id', trade_idx)}", help="Permanently delete this trade record"):
                            if delete_trade(selected_trade.get('id'), logs_dir=None):
                                st.success(f"✅ Trade deleted successfully")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete trade")
                
                # Calculate symbol statistics
                sym_stats = {
                    "Total Trades": len(symbol_trades),
                    "Total Profit": sum(t["pnl"] for t in symbol_trades if t["pnl"] > 0),
                    "Total Loss": sum(abs(t["pnl"]) for t in symbol_trades if t["pnl"] < 0),
                    "Win Rate": (len([t for t in symbol_trades if t["pnl"] > 0]) / len(symbol_trades) * 100) if symbol_trades else 0,
                    "Avg P&L %": sum(t["pnl_pct"] for t in symbol_trades) / len(symbol_trades) if symbol_trades else 0,
                }
                
                st.divider()
                st.markdown(f"**{selected_sym} Overall Statistics**")
                scol1, scol2, scol3, scol4 = st.columns(4)
                with scol1:
                    st.metric("Trades", sym_stats["Total Trades"])
                with scol2:
                    st.metric("Profit", f"Rs. {sym_stats['Total Profit']:,.2f}")
                with scol3:
                    st.metric("Loss", f"Rs. {sym_stats['Total Loss']:,.2f}")
                with scol4:
                    st.metric("Win Rate", f"{sym_stats['Win Rate']:.1f}%")
    else:
        st.info("📊 No trades recorded yet. Once you sell a position, it will appear here.")
