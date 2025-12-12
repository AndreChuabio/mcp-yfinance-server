#!/usr/bin/env python3
"""
Paper Invest Setup Helper - Interactive configuration tool
"""

import os
from pathlib import Path


def check_env_file():
    """Check if .env file exists"""
    env_path = Path(__file__).parent.parent / '.env'
    return env_path.exists(), env_path


def get_current_credentials():
    """Get current credentials from environment"""
    from dotenv import load_dotenv
    load_dotenv()

    return {
        'api_key': os.getenv('paper_API_KEY', ''),
        'account_id': os.getenv('paper_account_ID', ''),
        'portfolio_id': os.getenv('paper_portfolio_ID', '')
    }


def update_env_file(api_key, account_id, portfolio_id):
    """Update .env file with new credentials"""
    env_exists, env_path = check_env_file()

    if not env_exists:
        print(f"Creating .env file at {env_path}")
        # Copy from example
        example_path = env_path.parent / '.env.example'
        if example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)

    # Read current content
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Update credentials
    updated_lines = []
    keys_found = set()

    for line in lines:
        if line.startswith('paper_API_KEY='):
            updated_lines.append(f'paper_API_KEY={api_key}\n')
            keys_found.add('api_key')
        elif line.startswith('paper_account_ID='):
            updated_lines.append(f'paper_account_ID={account_id}\n')
            keys_found.add('account_id')
        elif line.startswith('paper_portfolio_ID='):
            updated_lines.append(f'paper_portfolio_ID={portfolio_id}\n')
            keys_found.add('portfolio_id')
        else:
            updated_lines.append(line)

    # Add missing keys at the end if needed
    if 'api_key' not in keys_found:
        updated_lines.append(f'\npaper_API_KEY={api_key}\n')
    if 'account_id' not in keys_found:
        updated_lines.append(f'paper_account_ID={account_id}\n')
    if 'portfolio_id' not in keys_found:
        updated_lines.append(f'paper_portfolio_ID={portfolio_id}\n')

    # Write back
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)

    print(f"\n✅ Credentials saved to {env_path}")


def main():
    """Interactive setup"""
    print("=" * 60)
    print("Paper Invest Setup Helper")
    print("=" * 60)
    print()

    # Check current status
    env_exists, env_path = check_env_file()

    if not env_exists:
        print("⚠️  No .env file found")
    else:
        print(f"✅ Found .env file at: {env_path}")

        current = get_current_credentials()
        print("\nCurrent Configuration:")
        print(
            f"  API Key: {'*' * 20}{current['api_key'][-4:] if len(current['api_key']) > 4 else 'NOT SET'}")
        print(
            f"  Account ID: {current['account_id'] if current['account_id'] else 'NOT SET'}")
        print(
            f"  Portfolio ID: {current['portfolio_id'] if current['portfolio_id'] else 'NOT SET'}")

    print("\n" + "=" * 60)
    print("Paper Invest Credential Setup")
    print("=" * 60)
    print()
    print("To get your credentials:")
    print("1. Log in to https://paperinvest.io")
    print("2. Go to Settings > API Keys and create a new key")
    print("3. Find your Account ID and Portfolio ID in the dashboard")
    print()
    print("Enter your credentials below (press Enter to skip):")
    print()

    # Get credentials
    api_key = input("Paper Invest API Key: ").strip()
    if not api_key and env_exists:
        api_key = get_current_credentials()['api_key']

    account_id = input("Account ID: ").strip()
    if not account_id and env_exists:
        account_id = get_current_credentials()['account_id']

    portfolio_id = input("Portfolio ID: ").strip()
    if not portfolio_id and env_exists:
        portfolio_id = get_current_credentials()['portfolio_id']

    if not api_key or not account_id or not portfolio_id:
        print("\n⚠️  Missing required credentials. Setup incomplete.")
        print("\nYou can manually edit .env file to add:")
        print("  paper_API_KEY=your_key_here")
        print("  paper_account_ID=your_account_id_here")
        print("  paper_portfolio_ID=your_portfolio_id_here")
        return

    # Update .env file
    update_env_file(api_key, account_id, portfolio_id)

    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    print()
    print("1. Verify configuration:")
    print("   python tests/test_paper_trading.py")
    print()
    print("2. Run a complete demo:")
    print("   python tests/demo_complete.py")
    print()
    print("3. Read the setup guide:")
    print("   cat docs/PAPER_TRADING_SETUP.md")
    print()
    print("✨ Setup complete")


if __name__ == "__main__":
    main()
