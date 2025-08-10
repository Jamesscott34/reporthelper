# Document Generator - Java Application

This directory contains the Java application responsible for generating professional PDF and Word documents from text content in the Report AI system.

## Overview

The `DocumentGenerator` is a standalone Java application that converts plain text content into well-formatted documents. It supports both PDF (using iText) and Word DOCX (using Apache POI) formats with automatic formatting and professional styling.

## Features

- **PDF Generation**: High-quality PDF documents with professional typography
- **Word Generation**: Modern DOCX files compatible with Microsoft Word
- **Automatic Formatting**: Intelligent detection and styling of section headers
- **Professional Output**: Consistent spacing, fonts, and layout
- **Cross-platform**: Runs on Windows, macOS, and Linux
- **UTF-8 Support**: Full international character support

## Prerequisites

### Required Software
- **Java 11 or higher** - Runtime environment
- **Maven 3.6 or higher** - Build and dependency management

### Verify Installation
```bash
# Check Java version
java -version

# Check Maven version
mvn -version
```

## Building the Application

### Option 1: Using Build Script (Windows)
```bash
# Navigate to java_assets directory
cd java_assets

# Run the build script
build.bat
```

### Option 2: Manual Maven Build
```bash
# Navigate to java_assets directory
cd java_assets

# Clean previous builds
mvn clean

# Compile the source code
mvn compile

# Package into executable JAR
mvn package
```

### Build Output
After successful build, you'll find:
- **Compiled classes**: `target/classes/`
- **Executable JAR**: `target/document-generator-1.0.0.jar`
- **Source JAR**: `target/document-generator-1.0.0-sources.jar`

## Running the Application

### Basic Usage
```bash
java -jar target/document-generator-1.0.0.jar <document_type> <file_format> <input_file> <output_file>
```

### Parameters
| Parameter | Description | Values |
|-----------|-------------|---------|
| `document_type` | Type of document being generated | `breakdown` or `report` |
| `file_format` | Output file format | `pdf` or `docx` |
| `input_file` | Path to text file containing content | Any text file path |
| `output_file` | Path where generated document will be saved | Output file path |

### Examples
```bash
# Generate PDF breakdown
java -jar target/document-generator-1.0.0.jar breakdown pdf input.txt breakdown.pdf

# Generate Word report
java -jar target/document-generator-1.0.0.jar report docx input.txt report.docx

# Generate PDF report
java -jar target/document-generator-1.0.0.jar report pdf content.txt report.pdf
```

## Input File Format

The application expects a plain text file with the following structure:

```
1. Executive Summary
This is the executive summary content that provides an overview of the document.

2. Detailed Analysis
This section contains detailed analysis with multiple paragraphs of content.

3. Key Findings
Important findings and observations are listed here.

4. Recommendations
Specific recommendations and next steps are outlined in this section.
```

### Formatting Rules
- **Section Headers**: Lines starting with numbers followed by periods (e.g., "1. Section Name")
- **Content**: Regular text content below headers
- **Spacing**: Empty lines are preserved for readability
- **Encoding**: UTF-8 encoding is supported for international characters

## Output Formats

### PDF Documents
- **Page Size**: A4 (210mm × 297mm)
- **Fonts**: Helvetica family (Bold for headers, Regular for content)
- **Styling**: Professional typography with consistent spacing
- **Features**: Automatic section detection, centered titles, timestamp footer

### Word Documents (DOCX)
- **Format**: Modern Office Open XML (Word 2007+)
- **Fonts**: Arial family with professional styling
- **Features**: Editable content, consistent formatting, cross-platform compatibility
- **Styling**: Automatic header detection, proper spacing, professional colors

## Integration with Report AI

### Django Integration
The Java application is called from Django views using subprocess:

```python
# Example from Django view
result = subprocess.run([
    'java', '-jar', 'java_assets/DocumentGenerator.jar',
    document_type, file_format, temp_content_path, output_path
], capture_output=True, text=True)
```

### File Flow
1. **Django**: Prepares content and calls Java application
2. **Java**: Generates document in specified format
3. **File System**: Document is saved to media directory
4. **User**: Downloads generated document via web interface

## Development and Customization

### Project Structure
```
java_assets/
├── DocumentGenerator.java    # Main application class
├── pom.xml                  # Maven configuration
├── build.bat               # Windows build script
├── README.md               # This documentation
└── target/                 # Build output (after compilation)
```

### Adding New Features
1. **Modify Source**: Edit `DocumentGenerator.java`
2. **Add Dependencies**: Update `pom.xml` if needed
3. **Rebuild**: Run `mvn clean package`
4. **Test**: Verify functionality with sample content

### Customizing Output
- **Fonts**: Modify font family and size in generation methods
- **Colors**: Adjust color schemes for headers and content
- **Spacing**: Customize spacing between elements
- **Layout**: Modify page margins and document structure

## Troubleshooting

### Common Issues

#### 1. Java Not Found
```bash
Error: 'java' is not recognized as an internal or external command
```
**Solution**: Ensure Java is installed and added to PATH environment variable.

#### 2. Maven Not Found
```bash
Error: 'mvn' is not recognized as an internal or external command
```
**Solution**: Install Maven and add to PATH, or use the build script.

#### 3. Compilation Errors
```bash
Error: package com.itextpdf.text does not exist
```
**Solution**: Run `mvn clean compile` to download dependencies.

#### 4. Runtime Errors
```bash
Error: Could not find or load main class DocumentGenerator
```
**Solution**: Ensure the JAR file was built correctly with `mvn package`.

### Debug Mode
Enable verbose output during build:
```bash
mvn clean package -X
```

### Logging
The application provides detailed console output:
- File reading progress
- Generation status
- Output file information
- Error details with stack traces

## Performance Considerations

### Memory Usage
- **PDF Generation**: Efficient memory usage with iText
- **Word Generation**: Apache POI optimized for large documents
- **File Processing**: Stream-based processing for large content

### Processing Time
- **Small Documents** (< 1MB): < 1 second
- **Medium Documents** (1-10MB): 1-5 seconds
- **Large Documents** (> 10MB): 5-30 seconds

### Optimization Tips
- Use appropriate input file sizes
- Avoid extremely long lines in input
- Process documents in batches if needed

## Security Considerations

### File Access
- **Input Validation**: All file paths are validated
- **Output Security**: Files are written to specified locations only
- **Resource Management**: Proper cleanup of temporary resources

### Dependencies
- **iText**: Mature, well-tested PDF library
- **Apache POI**: Apache Foundation project with security focus
- **Regular Updates**: Keep dependencies updated for security patches

## Contributing

### Code Style
- Follow Java coding conventions
- Use meaningful variable and method names
- Add comprehensive JavaDoc comments
- Include error handling for all operations

### Testing
- Test with various input file sizes
- Verify output quality in different formats
- Test cross-platform compatibility
- Validate integration with Django system

### Documentation
- Keep this README updated
- Document any new features
- Include usage examples
- Maintain troubleshooting section

## License

This project is licensed under the Apache License, Version 2.0. See the LICENSE file for details.

## Support

For issues and questions:
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check this README and inline code comments
- **Development Team**: Contact the Report AI development team

## Version History

- **v1.0.0**: Initial release with PDF and Word generation support
- Basic formatting and section detection
- Professional styling and typography
- Cross-platform compatibility
