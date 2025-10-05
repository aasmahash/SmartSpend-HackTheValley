import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:hackaton_app/dashboard.dart'; 


class UploadCSVPage extends StatefulWidget {
  const UploadCSVPage({super.key});


  @override
  State<UploadCSVPage> createState() => _UploadCSVPageState();
}


class _UploadCSVPageState extends State<UploadCSVPage> {
  List<PlatformFile> uploadedFiles = [];


  Future<void> _pickCSVFiles() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['csv'],
        allowMultiple: true,
        withData: true,
      );


      if (result == null) return; // user cancelled


      List<PlatformFile> picked = result.files
          .where((f) => f.extension?.toLowerCase() == 'csv')
          .toList();


      final remainingSlots = 3 - uploadedFiles.length;
      picked = picked.take(remainingSlots).toList();


      final nonDuplicates = picked.where(
        (f) => uploadedFiles.every((existing) => existing.name != f.name),
      );


      setState(() {
        uploadedFiles.addAll(nonDuplicates);
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error picking files: $e')),
      );
    }
  }


  void _removeFile(PlatformFile file) {
    setState(() {
      uploadedFiles.remove(file);
    });
  }


  Future<void> _uploadToBackend() async {
    final uri = Uri.parse("http://127.0.0.1:3000/upload");
    final request = http.MultipartRequest('POST', uri);


    for (final file in uploadedFiles) {
      if (file.bytes != null) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'files',
            file.bytes!,
            filename: file.name,
          ),
        );
      }
    }

    Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const DashboardPage()),
        );




    final response = await request.send();


    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Files uploaded successfully!")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Upload failed: ${response.statusCode}")),
      );
    }
  }


  Widget _buildEmptyUploadBox() {
    return GestureDetector(
      onTap: _pickCSVFiles,
      child: Center(
        child: Container(
          width: 700,
          height: 400,
          decoration: BoxDecoration(
            color: const Color(0xFFF2F4F7),
            borderRadius: BorderRadius.circular(16),
          ),
          child: const Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.upload_outlined, size: 40, color: Colors.black54),
                SizedBox(height: 12),
                Text(
                  'Click here to upload\nSupported Format: CSV',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 15,
                    color: Colors.black54,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }


  Widget _buildUploadedFilesBox() {
    return Column(
      children: [
        Center(
          child: Container(
            width: 700,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFF2F4F7),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Uploaded Files:',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const SizedBox(height: 8),
                ...uploadedFiles.map((file) {
                  return Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          file.name,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 14),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.delete_outline, color: Colors.red),
                        onPressed: () => _removeFile(file),
                      ),
                    ],
                  );
                }),
                if (uploadedFiles.length < 3) ...[
                  const Divider(),
                  Center(
                    child: TextButton.icon(
                      onPressed: _pickCSVFiles,
                      icon: const Icon(Icons.add),
                      label: const Text('Add more'),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        Center(
          child: ElevatedButton.icon(
            onPressed: _uploadToBackend,
            icon: const Icon(Icons.arrow_forward),
            label: const Text('Proceed'),
           
          ),
        )
      ],
    );
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: SingleChildScrollView( // ✅ Fix overflow
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const SizedBox(height: 20),
                const Text(
                  'Upload CSV',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Upload 1 to 3 CSV files\nof your recent credit card statements\nto get started.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 15,
                    color: Colors.grey,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 40),
                uploadedFiles.isEmpty
                    ? _buildEmptyUploadBox()
                    : _buildUploadedFilesBox(),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
