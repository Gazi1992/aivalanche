# theme.py

import sys

# --- Central Theme Control (Light Theme) ---
theme_colors = {
    "background": "#F0F0F0",          # Light gray background overall
    "foreground": "#1E1E1E",          # Dark gray text overall
    "primary": "#007ACC",             # Primary accent color (blue)
    "secondary": "#E0E0E0",         # Lighter gray for separators, hover backgrounds
    "sidebar_background": "#FFFFFF", # Use white for card background and nav sidebar
    "button_hover": "#005C99",        # Darker blue on hover for primary buttons
    "list_selected_background": "#007ACC", # Background of selected item in sidebar list
    "list_selected_text": "#FFFFFF",     # Text color for selected item in sidebar list
    "connected_status": "#28A745",     # Slightly brighter green for connected status
    "disconnected_status": "#B0B0B0",   # Gray for disconnected status in cards
    "compact_disconnected_status": "#DC3545", # Red for disconnected status in compact view
    "card_description": "#4A4A4A",     # Slightly darker gray for card description text
    "card_border": "#D8D8D8",         # Lighter border color for instrument card
    # "placeholder_bg": "#E8E8E8",      # REMOVED - No longer drawing placeholder
    # Chat specific colors
    "chat_title": "#333333",          # More neutral dark gray for chat title
    "chat_input_bg": "#FFFFFF",       # White background for chat input container
    "chat_send_button_bg": "#007ACC", # Use primary blue for chat send button
    "chat_send_button_hover": "#005C99",# Use primary hover for chat send button
    "chat_placeholder_text": "#AAAAAA", # Color for placeholder text in chat input
    # Compact bar colors
    "compact_separator": "#D0D0D0",     # Color for the separator line in compact view
    "compact_empty_text": "#B0B0B0"    # Muted color for "None" text
}

# Generate a basic stylesheet using the theme colors
def generate_stylesheet(colors):
    """Generates the Qt Style Sheet (QSS) string based on the theme colors."""

    # Ensure all required keys are present
    required_keys = [
        "background", "foreground", "primary", "secondary",
        "sidebar_background", "button_hover", "list_selected_background",
        "list_selected_text", "connected_status", "disconnected_status",
        "compact_disconnected_status", "card_description", "card_border",
        # "placeholder_bg", # REMOVED
        # Chat keys
        "chat_title", "chat_input_bg", "chat_send_button_bg",
        "chat_send_button_hover", "chat_placeholder_text",
        # Compact bar keys
        "compact_separator", "compact_empty_text"
    ]
    missing_keys = [key for key in required_keys if key not in colors]
    if missing_keys:
        raise ValueError(f"Theme color dictionary is missing required keys: {', '.join(missing_keys)}")

    # --- QSS String ---
    return f"""
        /* --- Global Defaults --- */
        QWidget {{
            background-color: {colors['background']};
            color: {colors['foreground']};
            font-size: 10pt;
        }}
        QMainWindow {{ background-color: {colors['background']}; }}
        QMainWindow::separator {{ background: {colors['primary']}; width: 2px; height: 2px; }}

        /* --- Dock Widget (Navigation Sidebar) --- */
        QDockWidget {{ border: none; color: {colors['foreground']}; }}
        QDockWidget > QWidget#NavBarContainer {{
             background-color: {colors['sidebar_background']}; /* White */
             border: none; padding: 5px;
        }}
        QDockWidget::title {{ height: 0px; border: 0px; padding: 0px; margin: 0px; background: {colors['sidebar_background']}; }}

        /* --- Stacked Widget (Main Content Area) --- */
        QStackedWidget > QWidget {{ background-color: {colors['background']}; }}

        /* --- Generic Widgets --- */
        QLabel {{ background-color: transparent; color: {colors['foreground']}; padding: 1px; }}
        QLineEdit {{ padding: 5px 8px; border: 1px solid {colors['card_border']}; border-radius: 4px; background-color: {colors['chat_input_bg']}; color: {colors['foreground']}; min-height: 24px; }}
        QLineEdit:focus {{ border: 1px solid {colors['primary']}; }}
        QPushButton {{ padding: 6px 15px; background-color: {colors['primary']}; color: {colors['list_selected_text']}; border: none; border-radius: 4px; font-weight: normal; min-height: 24px; }}
        QPushButton:hover {{ background-color: {colors['button_hover']}; }}
        QTextEdit {{ background-color: {colors['chat_input_bg']}; color: {colors['foreground']}; border: 1px solid {colors['card_border']}; border-radius: 4px; padding: 5px; }}
        QScrollArea {{ border: none; background-color: transparent; }}
        QScrollArea > QWidget > QWidget {{ background-color: transparent; }}


        /* --- Navigation Bar Content --- */
        #NavHeaderIcon {{ margin-bottom: 4px; }}
        #NavHeaderText {{ font-size: 14pt; font-weight: 600; color: {colors['primary']}; }}
        #NavSeparator {{ margin-top: 12px; margin-bottom: 10px; }}
        #NavSeparator[frameShape="4"] {{ border: none; border-top: 1px solid {colors['secondary']}; max-height: 1px; }}
        QListWidget#NavList {{ background-color: transparent; border: none; outline: 0; padding: 0px; }}
        QListWidget#NavList::item {{ color: {colors['foreground']}; padding: 10px 15px; border-radius: 4px; margin-bottom: 3px; background-color: transparent; }}
        QListWidget#NavList::item:hover {{ background-color: {colors['secondary']}; }}
        QListWidget#NavList::item:selected {{ background-color: {colors['list_selected_background']}; color: {colors['list_selected_text']}; font-weight: bold; }}

        /* --- Generic Content Page Label Styling --- */
        #ContentPage QLabel {{ padding: 15px; font-size: 12pt; alignment: 'AlignCenter'; }}

        /* --- Instrument Page Specific Styles --- */
        #InstrumentsPage {{ }}
        #SearchInput {{ }}
        #DiscoverButton {{ font-weight: bold; }}

        /* Style for the container holding the sticky category titles */
        #CategoryHeaderContainer {{
            /* background-color: #FAFAFA; */ /* Optional distinct background */
            border-bottom: 1px solid {colors['card_border']}; /* Separator line below titles */
            padding-bottom: 5px; /* Space below titles before the line */
        }}
        /* Style for the individual title labels in the header row */
        #CategoryHeaderLabel {{
            color: {colors['primary']};
            font-weight: bold;
            font-size: 11pt;
            padding: 3px 0px; /* Vertical padding */
            /* text-align: center; */ /* Optional: Center text */
            /* Fixed width set in code */
        }}

        #InstrumentScrollArea {{ border: none; /* Clean look */ }}
        #ScrollContentContainer {{ /* Container inside scroll area */ }}

        /* Style for the column widget holding cards */
        #InstrumentColumnWidget {{
            padding-top: 5px; /* Add space above the first card in column */
        }}
        /* Label shown inside column if no instruments (fallback) */
        #EmptyColumnLabel {{
             color: {colors['disconnected_status']};
             font-style: italic;
             padding: 10px 5px;
             font-size: 9pt;
             text-align: center;
        }}


        /* --- Instrument Card Styling (Modern Look) --- */
        #InstrumentCard {{
            background-color: {colors['sidebar_background']}; /* White */
            border: 1px solid {colors['card_border']};
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 12px;
        }}
        #InstrumentCard #CardImage {{
             border-radius: 4px;
             margin-top: 8px;
             margin-bottom: 12px;
             min-height: 50px; /* Ensure some space if icon fails */
             /* Background color removed, relies on icon/fallback text */
        }}
         #InstrumentCard QLabel {{ background-color: transparent; color: {colors['foreground']}; padding: 1px; font-size: 10pt; font-weight: normal; word-wrap: break-word; }}
         #InstrumentCard #CardName {{ font-weight: 600; font-size: 12pt; color: {colors['foreground']}; margin-bottom: 0px; }}
         #InstrumentCard #CardDescription {{ color: {colors['card_description']}; font-size: 9pt; line-height: 1.4; margin-bottom: 8px; text-align: center; }}
         #InstrumentCard #CardStatus {{ font-size: 9pt; font-weight: 600; }}
         #InstrumentCard #CardStatus[connectionStatus="connected"] {{ color: {colors['connected_status']}; }}
         #InstrumentCard #CardStatus[connectionStatus="disconnected"] {{ color: {colors['disconnected_status']}; }}
         #InstrumentCard #ConnectButton {{ padding: 5px 12px; font-size: 9pt; font-weight: 500; min-height: 30px; border-radius: 5px; background-color: {colors['primary']}; color: {colors['list_selected_text']}; }}
         #InstrumentCard #ConnectButton:hover {{ background-color: {colors['button_hover']}; }}
        /* Label shown in header/columns if loading fails or no categories found */
        #EmptyCategoryLabel {{ color: {colors['foreground']}; font-style: italic; padding: 10px 0px; font-size: 9pt; }}


        /* --- Compact Instrument Bar Styles (in ChatPage) --- */
        #ChatTopBarContainer {{ border-bottom: 1px solid {colors['card_border']}; padding-bottom: 8px; }}
        #ChatTopBarTitle {{ font-size: 10pt; font-weight: 600; color: {colors['foreground']}; margin-bottom: 4px; }}
        #InstrumentBarContent {{ background-color: transparent; }}
        #CompactCategoryWidget {{ }}
        #CompactCategoryTitle {{ font-size: 9pt; font-weight: 600; color: {colors['primary']}; margin-bottom: 3px; padding-left: 2px; }}
        #CompactCategorySeparator {{ margin-bottom: 4px; }}
        #CompactCategorySeparator[frameShape="4"] {{ border: none; border-top: 1px solid {colors['compact_separator']}; max-height: 1px; }}
        #CompactInstrumentWidget {{ }}
        #CompactStatusIcon {{ margin-right: 2px; }}
        #CompactInstrumentName {{ font-size: 9pt; color: {colors['foreground']}; }}
        #CompactEmptyLabel {{ font-size: 8pt; font-style: italic; color: {colors['compact_empty_text']}; padding-left: 15px; }}


        /* --- Chat Page Styles --- */
        #ChatPage {{ }}
        #ChatTitleLabel {{ color: {colors['chat_title']}; font-size: 18pt; margin-bottom: 20px; margin-top: 10px; }}
        #ChatInputContainer {{ background-color: {colors['chat_input_bg']}; border: 1px solid {colors['card_border']}; border-radius: 12px; max-width: 600px; }}
        #ChatInputArea {{ background-color: transparent; border: none; color: {colors['foreground']}; font-size: 11pt; padding: 8px; }}
        #ChatInputArea::placeholder {{ color: {colors['chat_placeholder_text']}; }}
        #ChatInputArea QScrollBar:vertical {{ border: none; background: {colors['background']}; width: 8px; margin: 0px; }}
        #ChatInputArea QScrollBar::handle:vertical {{ background: {colors['secondary']}; min-height: 20px; border-radius: 4px; }}
        #ChatInputArea QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        #ChatInputArea QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        #ChatSendButton {{ background-color: {colors['chat_send_button_bg']}; border: none; border-radius: 8px; color: {colors['list_selected_text']}; padding: 0px; min-width: 36px; max-width: 36px; min-height: 36px; max-height: 36px; }}
        #ChatSendButton:hover {{ background-color: {colors['chat_send_button_hover']}; }}
        #ChatSendButton:pressed {{ background-color: {colors['primary']}; }}

    """ # End of the f-string

# Example of how to use it (this part won't run unless theme.py is executed directly)
if __name__ == '__main__':
    try:
        stylesheet = generate_stylesheet(theme_colors)
        print("Stylesheet generated successfully:")
        print("-" * 30)
        print(stylesheet)
        print("-" * 30)
    except ValueError as e:
        print(f"Error generating stylesheet: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
