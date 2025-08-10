# Document Generation and Saving Features

This document explains how to use the new document generation and saving features in the Report AI system.

## Overview

The system now supports:
1. **Saving Breakdowns** - Save AI-generated breakdowns as PDF or Word documents
2. **Generating Reports** - Create comprehensive reports with references and image placeholders
3. **Java Integration** - Uses Java backend for high-quality PDF and Word document generation

## Features

### Save Breakdown
- Saves the current breakdown content as a PDF or Word document
- Filename format: `originalname_breakdown.pdf` or `originalname_breakdown.docx`
- Preserves all section formatting and content structure

### Generate & Save Report
- Creates a comprehensive report reviewing the extracted text and breakdown
- Includes detailed analysis with references
- Adds image placeholders where visual content is needed
- Saves as PDF or Word document
- Filename format: `originalname_report.pdf` or `originalname_report.docx`

## How to Use

### 1. Access the Breakdown Viewer
Navigate to any breakdown in the system to see the new save buttons.

### 2. Save Breakdown
- Click either "Save as PDF" or "Save as Word" under "Save Breakdown"
- The system will generate the document and provide a download link
- Files are saved with the naming convention: `originalname_breakdown.[format]`

### 3. Generate and Save Report
- Click either "Save Report as PDF" or "Save Report as Word" under "Generate & Save Report"
- The system will:
  - Generate a comprehensive report using AI
  - Create the document in the selected format
  - Provide a download link
  - Display the report content in the viewer
- Files are saved with the naming convention: `originalname_report.[format]`

## Technical Details

### Backend Integration
- **Django Views**: Handle document generation requests
- **AI Service**: Generates comprehensive reports with references
- **Java Integration**: Creates high-quality PDF and Word documents

### Java Dependencies
The Java application requires:
- **iText**: For PDF generation
- **Apache POI**: For Word document generation
- **Java 11+**: Runtime environment

### File Generation Process
1. Frontend sends save request with document type and format
2. Backend prepares content and calls Java application
3. Java generates the document file
4. File is saved to media directory and made available for download
5. Success response includes download URL

## Building the Java Application

### Prerequisites
- Java 11 or higher
- Maven 3.6 or higher

### Build Steps
1. Navigate to the `java_assets` directory
2. Run the build script:
   - **Windows**: `build.bat`
   - **Linux/Mac**: `mvn clean package`
3. The JAR file will be created in `target/document-generator-1.0.0.jar`

### Manual Build
```bash
cd java_assets
mvn clean compile package
```

## Report Content Structure

The generated reports include:

### Sections
- **Executive Summary**: Overview of findings
- **Detailed Analysis**: In-depth breakdown of content
- **Key Insights**: Important discoveries and observations
- **Recommendations**: Suggested actions or next steps

### References
- Source citations for claims and data
- Bibliography of referenced materials
- Cross-references between sections

### Image Placeholders
- Visual content indicators
- Description of required images
- Placement suggestions

## File Formats

### PDF Documents
- Professional formatting with proper fonts
- Section headers and content organization
- Footer with generation timestamp
- Optimized for printing and sharing

### Word Documents
- Editable format for further customization
- Consistent styling and formatting
- Section breaks and spacing
- Compatible with Microsoft Word and other editors

## Troubleshooting

### Common Issues

1. **Java Not Found**
   - Ensure Java 11+ is installed and in PATH
   - Check `java -version` command

2. **Maven Not Found**
   - Install Maven and add to PATH
   - Verify with `mvn -version`

3. **Document Generation Fails**
   - Check Java application logs
   - Verify file permissions in media directory
   - Ensure sufficient disk space

4. **Report Generation Errors**
   - Check AI service connectivity
   - Verify breakdown content exists
   - Review error messages in browser console

### Debug Mode
Enable debug logging in Django settings to see detailed error information.

## Configuration

### Media Directory
Generated documents are saved to `media/generated_documents/` by default.

### File Size Limits
- Maximum input content: 10MB
- Generated file formats: PDF, DOCX
- Output quality: High resolution, print-ready

## Security Considerations

- Generated files are stored in the media directory
- Access control follows Django's file serving policies
- Temporary files are cleaned up after processing
- User authentication required for document generation

## Future Enhancements

- Custom document templates
- Batch document generation
- Email delivery of generated documents
- Document versioning and history
- Advanced formatting options
- Integration with cloud storage services
