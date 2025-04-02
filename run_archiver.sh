#!/bin/bash
# News Magazine Archiver

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found! Please install Python 3.6 or higher."
    exit 1
fi

# Main menu function
main_menu() {
    clear
    echo "News Magazine Archiver"
    echo "======================"
    echo
    echo "Main Menu"
    echo "========="
    echo "1. The Atlantic"
    echo "2. The Economist"
    echo "3. Set your Readwise API token"
    echo "4. Exit"
    echo

    read -p "Enter your choice (1-4): " main_choice

    case $main_choice in
        1)
            atlantic_menu
            ;;
        2)
            economist_menu
            ;;
        3)
            read -p "Enter your Readwise API token: " token
            python3 -c "from news_archiver.main import main; import sys; sys.argv.extend(['--token', '${token}']); main()"
            echo "Token set successfully."
            read -p "Press Enter to continue..." 
            main_menu
            ;;
        4)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice."
            read -p "Press Enter to continue..." 
            main_menu
            ;;
    esac
}

# Atlantic menu function
atlantic_menu() {
    clear
    echo "The Atlantic Menu"
    echo "================="
    echo "1. List available issues"
    echo "2. Archive a specific issue"
    echo "3. Interactive issue selection"
    echo "4. Back to main menu"
    echo

    read -p "Enter your choice (1-4): " choice

    case $choice in
        1)
            python3 -c "from news_archiver.main import main; import sys; sys.argv.extend(['--list-issues', '--source', 'atlantic']); main()"
            read -p "Press Enter to continue..." 
            atlantic_menu
            ;;
        2)
            read -p "Enter the exact issue name (e.g., 'April 2025'): " issue
            python3 -c "from news_archiver.main import main; import sys; sys.argv.extend(['--issue', '${issue}', '--source', 'atlantic']); main()"
            read -p "Press Enter to continue..." 
            atlantic_menu
            ;;
        3)
            python3 -c "from news_archiver.main import main; import sys; sys.argv.extend(['--source', 'atlantic']); main()"
            read -p "Press Enter to continue..." 
            atlantic_menu
            ;;
        4)
            main_menu
            ;;
        *)
            echo "Invalid choice."
            read -p "Press Enter to continue..." 
            atlantic_menu
            ;;
    esac
}

# Economist menu function
economist_menu() {
    clear
    echo "The Economist Menu"
    echo "=================="
    echo "1. List available issues"
    echo "2. Archive a specific issue"
    echo "3. Interactive issue selection"
    echo "4. Back to main menu"
    echo

    read -p "Enter your choice (1-4): " choice

    case $choice in
        1)
            python3 -c "from news_archiver.main import main; import sys; sys.argv.extend(['--list-issues', '--source', 'economist']); main()"
            read -p "Press Enter to continue..." 
            economist_menu
            ;;
        2)
            read -p "Enter the exact issue name (e.g., 'Mar 29th 2025'): " issue
            python3 -c "from news_archiver.main import main; import sys; sys.argv.extend(['--issue', '${issue}', '--source', 'economist']); main()"
            read -p "Press Enter to continue..." 
            economist_menu
            ;;
        3)
            python3 -c "from news_archiver.main import main; import sys; sys.argv.extend(['--source', 'economist']); main()"
            read -p "Press Enter to continue..." 
            economist_menu
            ;;
        4)
            main_menu
            ;;
        *)
            echo "Invalid choice."
            read -p "Press Enter to continue..." 
            economist_menu
            ;;
    esac
}

# Start the script
main_menu 