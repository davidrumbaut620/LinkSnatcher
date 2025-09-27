# Overview

This is a Flask-based web application called "Gestor de Descargas Web" (Web Download Manager) that functions as a comprehensive download manager similar to Internet Download Manager. The application scans any user-provided URL and extracts all direct file links (images, videos, PDFs, documents, archives, executables, and more), allowing users to download files directly to their device without any server-side storage. It features a modern, responsive web interface built with Tailwind CSS using a custom color scheme inspired by popular download managers like IDM and JDownloader.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Tailwind CSS for responsive design
- **Styling**: Custom Tailwind configuration with extended color palette and Inter font family
- **Layout**: Modern single-page application with header navigation and content sections

## Backend Architecture
- **Web Framework**: Flask with minimal configuration
- **Core Components**:
  - `FileScanner` class for file type detection and URL processing
  - File categorization system with predefined extension mappings
  - URL parsing and filename extraction utilities
- **Session Management**: Flask sessions with configurable secret key
- **Response Handling**: Support for JSON API responses and template streaming

## File Processing System
- **File Categorization**: Automatic classification into 7 categories (images, videos, audio, documents, archives, executables, others)
- **URL Analysis**: Extraction of filenames from URL paths and query parameters
- **Extension Mapping**: Comprehensive file extension database for type detection

## Web Scraping Capabilities
- **HTTP Client**: Requests library for web content fetching
- **HTML Parsing**: BeautifulSoup integration for DOM manipulation
- **URL Processing**: urllib for URL parsing and manipulation

# External Dependencies

## Python Libraries
- **Flask**: Web framework and templating
- **Requests**: HTTP client for web scraping
- **BeautifulSoup**: HTML/XML parsing and manipulation
- **urllib**: URL parsing and encoding utilities
- **mimetypes**: MIME type detection support

## Frontend Dependencies
- **Tailwind CSS**: Utility-first CSS framework via CDN
- **Google Fonts**: Inter font family for typography
- **Modern Browser APIs**: ES6+ JavaScript features

## Environment Configuration
- **SESSION_SECRET**: Configurable session secret key via environment variables
- **Flask Development Server**: Built-in development server support

## Web Standards
- **HTML5**: Modern semantic markup
- **CSS3**: Advanced styling with Tailwind utilities
- **HTTP/HTTPS**: Standard web protocols for content fetching
- **MIME Types**: Standard file type detection and categorization