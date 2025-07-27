# OLX Kazakhstan Commercial Real Estate Parser

A Python web scraper for extracting commercial real estate rental listings from OLX Kazakhstan (olx.kz). This tool is designed for data analysis and market research purposes.

## 🎯 Purpose

This parser extracts commercial property rental listings from OLX.kz, specifically targeting:
- Commercial spaces for rent
- Office buildings
- Retail spaces
- Warehouses and industrial properties

## ✨ Features

- **Configurable Settings**: YAML-based configuration for flexible operation
- **Debug Mode**: Extensive logging and debugging capabilities
- **Respectful Scraping**: Built-in delays and robots.txt compliance checking
- **Data Analysis**: Automatic filtering and statistical analysis of scraped data
- **Error Handling**: Robust error handling with fallback mechanisms
- **Multiple Selectors**: Uses multiple CSS selectors to handle website changes
- **CSV Export**: Saves results in CSV format for further analysis

## 📋 Requirements

Create a `requirements.txt` file with:

```
requests>=2.31.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
PyYAML>=6.0
lxml>=4.9.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `settings.yaml` file in the same directory:

```yaml
parser:
  max_pages:
    debug: 3      # Pages to scrape in debug mode
    production: 50 # Pages to scrape in production mode

network:
  request_timeout: 10  # Request timeout in seconds
  delays:
    min: 2  # Minimum delay between requests (seconds)
    max: 4  # Maximum delay between requests (seconds)
```

## 🚀 Usage

### Basic Usage

```python
from improved_parser import OLXParser

# Initialize parser in debug mode
parser = OLXParser(config_file='settings.yaml', debug_mode=True)

# Run the scraper
parser.run_debug()
```

### Command Line Usage

```bash
python improved_parser.py
```

## 📊 Data Structure

The parser extracts the following information for each listing:

| Field | Description | Type |
|-------|-------------|------|
| `title` | Property title/description | String |
| `price_text` | Raw price text from the website | String |
| `price_numeric` | Extracted numeric price in KZT | Float |
| `area` | Property area in square meters | Float |
| `location` | Property location/address | String |
| `link` | Full URL to the listing | String |

## 🔍 How It Works

### 1. Configuration Loading
- Loads settings from YAML file
- Provides sensible defaults if config is missing

### 2. Session Setup
- Configures HTTP session with realistic headers
- Rotates user agents to avoid detection
- Implements request delays and timeouts

### 3. Page Scraping
- Fetches listing pages sequentially
- Uses multiple CSS selectors for robustness
- Handles website structure changes gracefully

### 4. Data Extraction
- Extracts title, price, area, and location
- Cleans and normalizes extracted data
- Handles missing or malformed data

### 5. Analysis & Export
- Provides statistical analysis of scraped data
- Applies configurable filters
- Exports results to CSV format

## 📈 Built-in Analysis

The parser automatically analyzes scraped data:

- **Price Statistics**: Min, max, and average prices
- **Area Statistics**: Property size distributions
- **Location Analysis**: Most common locations
- **Filter Testing**: Tests predefined filters for relevant properties

## 🛡️ Ethical Considerations

This scraper is designed to be respectful:

- ✅ Checks `robots.txt` before scraping
- ✅ Implements delays between requests
- ✅ Uses realistic request headers
- ✅ Limits concurrent requests
- ✅ Designed for research purposes only

## 📂 Output Files

- `debug_results.csv`: Contains all scraped listings with extracted data
- Console logs with detailed debugging information

## 🔧 Customization

### Adding New Selectors

To handle website changes, add new CSS selectors in the extraction methods:

```python
# In _extract_listing_data_debug method
title_selectors = [
    'h6', 'h4', 'h3', 'h2', 'h1',
    '[data-cy="ad-card-title"]', 
    'a[data-cy="listing-ad-title"]',
    # Add new selectors here
]
```

### Modifying Filters

Adjust filters in the `analyze_data_debug` method:

```python
# Area filter (currently >= 50 sq meters)
area_filter_pass = len([l for l in listings if l['area'] and l['area'] >= 50])

# Price filter (currently <= 500,000 KZT)
price_filter_pass = len([l for l in listings if l['price_numeric'] and l['price_numeric'] <= 500000])
```

## 🚨 Troubleshooting

### Common Issues

1. **No data extracted**: Website structure may have changed
   - Check console logs for selector debugging info
   - Update CSS selectors as needed

2. **Connection errors**: Network issues or rate limiting
   - Increase delays in configuration
   - Check robots.txt compliance

3. **YAML errors**: Configuration file issues
   - Validate YAML syntax
   - Check file encoding (should be UTF-8)

### Debug Mode

Run in debug mode to see detailed information:
- Found elements count
- Selector success/failure
- Extracted data for each listing
- Page structure analysis

## 📄 License

This tool is for educational and research purposes only. Please respect OLX.kz's terms of service and use responsibly.

## ⚠️ Disclaimer

- This scraper is for educational and research purposes
- Respect website terms of service
- Don't overload servers with requests
- Consider using official APIs when available
- Be mindful of data privacy and usage rights

## 🤝 Contributing

To contribute:
1. Test with different configurations
2. Add new CSS selectors for robustness
3. Improve error handling
4. Add new analysis features

## 📞 Support

For issues or questions:
1. Check the console output in debug mode
2. Verify your configuration file
3. Ensure all dependencies are installed
4. Check network connectivity
