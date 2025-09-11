---
mode: agent
---
Define the task to achieve, including specific requirements, constraints, and success criteria.

# Task: Integrate Paper Trading API with MCP YFinance Server

## 🎯 Objective
Extend the existing MCP YFinance server to include paper trading functionality using the Paper Trading API. This will allow users to not only get stock data but also execute simulated trades, manage portfolio positions, and track trading performance in a risk-free environment.

## 📋 Requirements

### 1. Paper Trading API Integration
- Integrate with Paper Trading API using the provided credentials:
  - API Key: `d96932cbca85940a0d8332ba0df297bf26032fe04756ffef64488f666f2d02ba`
  - Account ID: `b2c75ae8-93e1-4339-b060-83a6a1eb4c60` 
  - Portfolio ID: `4996db29-73b2-42d9-a548-e3034aaa8451`
- Implement secure credential management through environment variables
- Add proper error handling for API calls

### 2. New MCP Tools to Implement

#### Portfolio Management
- **get_portfolio_balance** - Get current account balance and buying power
- **get_portfolio_positions** - Get all current stock positions
- **get_portfolio_history** - Get portfolio performance over time

#### Trading Operations  
- **place_buy_order** - Execute a buy order for specified stock and quantity
- **place_sell_order** - Execute a sell order for specified stock and quantity
- **get_order_status** - Check status of a specific order
- **get_order_history** - Get history of all orders

#### Analysis Tools
- **calculate_portfolio_metrics** - Calculate key performance metrics (total return, daily P&L, etc.)
- **get_position_performance** - Get performance data for specific positions

### 3. Technical Implementation

#### Dependencies
- Add required packages to `requirements.txt`:
  - `requests` (for API calls)
  - `python-dotenv` (for environment variable management)
  - Any paper trading specific SDK if available

#### Security
- Load API credentials from `.env` file
- Never expose credentials in logs or error messages
- Implement proper API rate limiting

#### Error Handling
- Handle network failures gracefully
- Provide meaningful error messages for failed trades
- Validate input parameters before API calls

## 🎛️ Configuration

### Environment Variables (.env)
```
paper_API_KEY=d96932cbca85940a0d8332ba0df297bf26032fe04756ffef64488f666f2d02ba
paper_account_ID=b2c75ae8-93e1-4339-b060-83a6a1eb4c60
paper_portfolio_ID=4996db29-73b2-42d9-a548-e3034aaa8451
```

### API Integration
- Base URL for Paper Trading API (research and implement)
- Authentication headers and request format
- Response parsing and error handling

## ✅ Success Criteria

### Functional Requirements
1. **Data Integration**: Seamlessly combine yfinance stock data with paper trading operations
2. **Portfolio Tracking**: Users can view real-time portfolio balance and positions
3. **Trade Execution**: Users can execute buy/sell orders through natural language commands
4. **Performance Analysis**: Users can track portfolio performance and individual position gains/losses

### Technical Requirements
1. **Reliability**: All API calls include proper error handling and retries
2. **Security**: Credentials are securely managed and never exposed
3. **Documentation**: All new tools are properly documented with examples
4. **Testing**: Unit tests for all new functionality

### User Experience
1. **Natural Language Interface**: Users can say things like:
   - "Buy 10 shares of AAPL"
   - "What's my current portfolio balance?"
   - "Show me my Tesla position performance"
   - "Sell half of my Microsoft shares"

2. **Informative Responses**: Clear, actionable information including:
   - Order confirmations with details
   - Current positions with P&L
   - Portfolio summaries with key metrics

## 🚀 Implementation Plan

### Phase 1: Setup and Authentication
1. Research Paper Trading API documentation
2. Set up API client with authentication
3. Create basic connection test

### Phase 2: Core Trading Functions
1. Implement portfolio query tools
2. Implement basic buy/sell order placement
3. Add order status and history tracking

### Phase 3: Enhanced Features
1. Add performance calculation tools
2. Implement portfolio analytics
3. Add comprehensive error handling

### Phase 4: Integration and Testing
1. Integrate with existing MCP server
2. Update documentation and examples
3. Create comprehensive test suite

## 📚 Additional Considerations

### Risk Management
- Implement position size limits
- Add confirmation prompts for large trades
- Include warnings about paper trading vs real trading

### Data Synchronization
- Ensure portfolio data stays in sync with trading operations
- Handle potential API rate limits gracefully

### User Education
- Provide clear documentation about paper trading limitations
- Include examples of common trading scenarios
- Add educational content about trading concepts 