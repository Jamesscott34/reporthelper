import java.io.FileOutputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Date;

import org.apache.poi.xwpf.usermodel.ParagraphAlignment;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.apache.poi.xwpf.usermodel.XWPFRun;

import com.itextpdf.text.BaseColor;
import com.itextpdf.text.Element;
import com.itextpdf.text.Font;
import com.itextpdf.text.FontFactory;
import com.itextpdf.text.PageSize;
import com.itextpdf.text.Paragraph;
import com.itextpdf.text.pdf.PdfWriter;

/**
 * DocumentGenerator - A Java application for generating professional PDF and Word documents
 * from text content with automatic formatting and styling.
 * 
 * <p>This class provides functionality to convert plain text content into well-formatted
 * documents suitable for business and academic use. It supports both PDF (using iText) and
 * Word DOCX (using Apache POI) formats.</p>
 * 
 * <p>The generator automatically detects section headers (numbered lists starting with "1.")
 * and applies appropriate styling to create a professional document structure.</p>
 * 
 * <h3>Usage:</h3>
 * <pre>
 * java DocumentGenerator &lt;document_type&gt; &lt;file_format&gt; &lt;input_file&gt; &lt;output_file&gt;
 * </pre>
 * 
 * <h3>Parameters:</h3>
 * <ul>
 *   <li><strong>document_type</strong>: Type of document ("breakdown" or "report")</li>
 *   <li><strong>file_format</strong>: Output format ("pdf" or "docx")</li>
 *   <li><strong>input_file</strong>: Path to text file containing content</li>
 *   <li><strong>output_file</strong>: Path where generated document will be saved</li>
 * </ul>
 * 
 * <h3>Example:</h3>
 * <pre>
 * java DocumentGenerator breakdown pdf input.txt breakdown.pdf
 * java DocumentGenerator report docx input.txt report.docx
 * </pre>
 * 
 * <h3>Features:</h3>
 * <ul>
 *   <li>Automatic section header detection and formatting</li>
 *   <li>Professional typography with appropriate fonts and spacing</li>
 *   <li>Automatic timestamp footer</li>
 *   <li>Cross-platform compatibility</li>
 *   <li>UTF-8 text encoding support</li>
 * </ul>
 * 
 * <h3>Dependencies:</h3>
 * <ul>
 *   <li>iText 5.5.13.3 - For PDF generation</li>
 *   <li>Apache POI 5.2.3 - For Word document generation</li>
 *   <li>Java 11+ - Runtime environment</li>
 * </ul>
 * 
 * @author Report AI System
 * @version 1.0.0
 * @since 2024
 */
public class DocumentGenerator {
    
    /**
     * Main entry point for the DocumentGenerator application.
     * 
     * <p>This method validates command line arguments, reads the input content,
     * and delegates document generation to the appropriate format handler.</p>
     * 
     * <p>The application expects exactly 4 arguments and will exit with an error
     * code if the arguments are invalid or if any errors occur during processing.</p>
     * 
     * @param args Command line arguments array containing:
     *             [0] document_type, [1] file_format, [2] input_file, [3] output_file
     * @throws IllegalArgumentException if arguments are invalid
     * @throws RuntimeException if document generation fails
     */
    public static void main(String[] args) {
        // Validate command line arguments
        if (args.length != 4) {
            System.err.println("Usage: java DocumentGenerator <document_type> <file_format> <input_file> <output_file>");
            System.err.println("  document_type: 'breakdown' or 'report'");
            System.err.println("  file_format: 'pdf' or 'docx'");
            System.err.println("  input_file: Path to text file with content");
            System.err.println("  output_file: Path for generated document");
            System.exit(1);
        }
        
        // Parse and validate arguments
        String documentType = args[0];  // "breakdown" or "report"
        String fileFormat = args[1];    // "pdf" or "docx"
        String inputFile = args[2];
        String outputFile = args[3];
        
        try {
            // Validate document type
            if (!documentType.equalsIgnoreCase("breakdown") && !documentType.equalsIgnoreCase("report")) {
                System.err.println("Error: document_type must be 'breakdown' or 'report', got: " + documentType);
                System.exit(1);
            }
            
            // Validate file format
            if (!fileFormat.equalsIgnoreCase("pdf") && !fileFormat.equalsIgnoreCase("docx")) {
                System.err.println("Error: file_format must be 'pdf' or 'docx', got: " + fileFormat);
                System.exit(1);
            }
            
            // Read input content from file
            System.out.println("Reading input content from: " + inputFile);
            String content = new String(Files.readAllBytes(Paths.get(inputFile)), "UTF-8");
            System.out.println("Content length: " + content.length() + " characters");
            
            // Generate document based on type and format
            System.out.println("Generating " + documentType + " document in " + fileFormat.toUpperCase() + " format...");
            if (fileFormat.equalsIgnoreCase("pdf")) {
                generatePDF(documentType, content, outputFile);
            } else if (fileFormat.equalsIgnoreCase("docx")) {
                generateWord(documentType, content, outputFile);
            }
            
            System.out.println("Document generated successfully: " + outputFile);
            System.out.println("Output file size: " + Files.size(Paths.get(outputFile)) + " bytes");
            
        } catch (Exception e) {
            System.err.println("Error generating document: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    /**
     * Generates a PDF document from the given content with professional formatting.
     * 
     * <p>This method creates a well-structured PDF document with the following features:</p>
     * <ul>
     *   <li>Professional title with centered alignment</li>
     *   <li>Automatic section header detection (numbered lists starting with "1.")</li>
     *   <li>Consistent typography and spacing</li>
     *   <li>Automatic footer with generation timestamp</li>
     *   <li>A4 page size with proper margins</li>
     * </ul>
     * 
     * <p>The method automatically detects section headers by looking for lines that
     * match the pattern "^\\d+\\..*" (lines starting with a number followed by a period).</p>
     * 
     * @param documentType The type of document being generated (used in title)
     * @param content The text content to include in the document
     * @param outputFile The file path where the PDF will be saved
     * @throws Exception if PDF generation fails (e.g., file I/O errors, PDF creation errors)
     */
    private static void generatePDF(String documentType, String content, String outputFile) throws Exception {
        // Create PDF document with A4 page size
        com.itextpdf.text.Document document = new com.itextpdf.text.Document(PageSize.A4);
        PdfWriter.getInstance(document, new FileOutputStream(outputFile));
        
        document.open();
        
        // Add document title with professional styling
        Font titleFont = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 18, BaseColor.BLACK);
        Paragraph title = new Paragraph(documentType.toUpperCase() + " DOCUMENT", titleFont);
        title.setAlignment(Element.ALIGN_CENTER);
        title.setSpacingAfter(20);
        document.add(title);
        
        // Process content line by line for intelligent formatting
        Font contentFont = FontFactory.getFont(FontFactory.HELVETICA, 12, BaseColor.BLACK);
        String[] lines = content.split("\n");
        
        for (String line : lines) {
            if (line.trim().isEmpty()) {
                // Add spacing for empty lines
                document.add(new Paragraph(" "));
            } else if (line.matches("^\\d+\\..*")) {
                // Format section headers (numbered lists starting with "1.")
                Font sectionFont = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 14, BaseColor.DARK_GRAY);
                Paragraph section = new Paragraph(line, sectionFont);
                section.setSpacingBefore(15);  // Space before section
                section.setSpacingAfter(10);   // Space after section
                document.add(section);
            } else {
                // Regular content paragraphs
                Paragraph paragraph = new Paragraph(line, contentFont);
                paragraph.setSpacingAfter(5);  // Small spacing between paragraphs
                document.add(paragraph);
            }
        }
        
        // Add professional footer with timestamp
        Font footerFont = FontFactory.getFont(FontFactory.HELVETICA, 10, BaseColor.GRAY);
        footerFont.setStyle(Font.ITALIC);
        Paragraph footer = new Paragraph("Generated on: " + new Date(), footerFont);
        footer.setAlignment(Element.ALIGN_CENTER);
        footer.setSpacingBefore(30);
        document.add(footer);
        
        document.close();
    }
    
    /**
     * Generates a Word document (DOCX) from the given content with professional formatting.
     * 
     * <p>This method creates a well-structured Word document with the following features:</p>
     * <ul>
     *   <li>Professional title with centered alignment</li>
     *   <li>Automatic section header detection and formatting</li>
     *   <li>Consistent typography using Arial font family</li>
     *   <li>Proper spacing and paragraph formatting</li>
     *   <li>Automatic footer with generation timestamp</li>
     *   <li>Compatible with Microsoft Word and other editors</li>
     * </ul>
     * 
     * <p>The method uses Apache POI to create a modern DOCX file with proper
     * OpenXML formatting and styling.</p>
     * 
     * @param documentType The type of document being generated (used in title)
     * @param content The text content to include in the document
     * @param outputFile The file path where the DOCX will be saved
     * @throws Exception if Word document generation fails (e.g., file I/O errors, POI errors)
     */
    private static void generateWord(String documentType, String content, String outputFile) throws Exception {
        // Create new Word document
        XWPFDocument document = new XWPFDocument();
        
        // Add document title with professional styling
        XWPFParagraph title = document.createParagraph();
        title.setAlignment(ParagraphAlignment.CENTER);
        XWPFRun titleRun = title.createRun();
        titleRun.setText(documentType.toUpperCase() + " DOCUMENT");
        titleRun.setBold(true);
        titleRun.setFontSize(18);
        titleRun.setFontFamily("Arial");
        
        // Add spacing after title
        document.createParagraph();
        
        // Process content line by line for intelligent formatting
        String[] lines = content.split("\n");
        
        for (String line : lines) {
            if (line.trim().isEmpty()) {
                // Add spacing for empty lines
                document.createParagraph();
            } else if (line.matches("^\\d+\\..*")) {
                // Format section headers (numbered lists starting with "1.")
                XWPFParagraph section = document.createParagraph();
                XWPFRun sectionRun = section.createRun();
                sectionRun.setText(line);
                sectionRun.setBold(true);
                sectionRun.setFontSize(14);
                sectionRun.setFontFamily("Arial");
                sectionRun.setColor("2F4F4F");  // Dark slate gray color
                section.setSpacingBefore(400);  // 20pt spacing before (400 = 20pt * 20)
                section.setSpacingAfter(200);   // 10pt spacing after (200 = 10pt * 20)
            } else {
                // Regular content paragraphs
                XWPFParagraph paragraph = document.createParagraph();
                XWPFRun run = paragraph.createRun();
                run.setText(line);
                run.setFontSize(12);
                run.setFontFamily("Arial");
                paragraph.setSpacingAfter(120);  // 6pt spacing after (120 = 6pt * 20)
            }
        }
        
        // Add professional footer with timestamp
        XWPFParagraph footer = document.createParagraph();
        footer.setAlignment(ParagraphAlignment.CENTER);
        XWPFRun footerRun = footer.createRun();
        footerRun.setText("Generated on: " + new Date());
        footerRun.setItalic(true);
        footerRun.setFontSize(10);
        footerRun.setFontFamily("Arial");
        footerRun.setColor("808080");  // Gray color
        footer.setSpacingBefore(600);  // 30pt spacing before (600 = 30pt * 20)
        
        // Save document to file with proper resource management
        try (FileOutputStream out = new FileOutputStream(outputFile)) {
            document.write(out);
        }
        
        document.close();
    }
}
