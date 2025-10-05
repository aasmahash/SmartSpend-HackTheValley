import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  _DashboardPageState createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  Future<Map<String, dynamic>> loadForecastData() async {
    final String response =
        await rootBundle.loadString('assets/forecast.json');
    return jsonDecode(response);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Forecast Chart")),
      body: FutureBuilder<Map<String, dynamic>>( // Ui build differently based on whether data is loaded or still loading
        future: loadForecastData(), //wati for async function to complete
        builder: (context, snapshot) { // snapshot --> provides the state of the connection
          if (!snapshot.hasData) { // makes sure chart is only built after data is loaded 
            return const Center(child: CircularProgressIndicator()); //show loading spinner
          }

          final data = snapshot.data!["forecast"]; // snapshot.data -> holds the actual result of the Future once it completes 
          // Before Future complete --> snapshot.hasData = false  
          // After Future completes successfully --> snapshot.data --. contains the Map form Json 
          // ! --> asserts it is not null 
          final List<String> dates = List<String>.from(data["dates"]); // convert JSON arrays to dart lists 
          final List<double> predicted =
              List<double>.from(data["predicted"].map((v) => v.toDouble())); // ensures values are doubles 
          final List<double> lower =
              List<double>.from(data["lower_bound"].map((v) => v.toDouble()));
          final List<double> upper =
              List<double>.from(data["upper_bound"].map((v) => v.toDouble()));

          final List<FlSpot> predictedSpots = List.generate( 
              predicted.length, (i) => FlSpot(i.toDouble(), predicted[i]));
              // FlSpot --> represents single data point in coordinate sys --> x, y 
          final List<FlSpot> lowerSpots =
              List.generate(lower.length, (i) => FlSpot(i.toDouble(), lower[i]));
          final List<FlSpot> upperSpots =
              List.generate(upper.length, (i) => FlSpot(i.toDouble(), upper[i]));

          final minY = [ ...lower, ...predicted, ...upper ].reduce((a, b) => a < b ? a : b); // lowest value in any list 
          final maxY = [ ...lower, ...predicted, ...upper ].reduce((a, b) => a > b ? a : b); // highest value 

          // Today index
          final todayIndex = dates.indexWhere((d) =>
              DateTime.parse(d).year == DateTime.now().year &&
              DateTime.parse(d).day == DateTime.now().day &&
              DateTime.parse(d).month == DateTime.now().month);

          return Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                Expanded(
                  child: LineChart(
                    LineChartData(
                      minY: minY - 50, // add margin (-50 / +50) -- make chart look nicer
                      maxY: maxY + 50,
                      gridData: FlGridData(show: true), 
                      titlesData: FlTitlesData(
                        bottomTitles: AxisTitles(
                          sideTitles: SideTitles(
                            showTitles: true,
                            interval: (dates.length / 5).floorToDouble(),
                            getTitlesWidget: (value, meta) {
                              int index = value.toInt();
                              if (index < 0 || index >= dates.length) {
                                return const SizedBox.shrink();
                              }
                              return Text(
                                dates[index],  // was dates[index].substring(5)
                                style: const TextStyle(fontSize: 10),
                              );
                            },
                          ),
                        ),
                        leftTitles: AxisTitles(
                          sideTitles: SideTitles(showTitles: true, reservedSize: 50),
                        ),
                      ),
                      borderData: FlBorderData(show: true),
                      lineBarsData: [
                        // Predicted line
                        LineChartBarData(
                          spots: predictedSpots,
                          isCurved: true,
                          color: Colors.blue,
                          barWidth: 3,
                          dotData: FlDotData(show: false),
                          dashArray: [5, 5],
                        ),

                        // Upper bound (for shading)
                        LineChartBarData(
                          spots: upperSpots,
                          isCurved: true,
                          color: Colors.transparent,
                          belowBarData: BarAreaData(
                            show: true,
                            color: Colors.blue.withOpacity(0.2),
                          ),
                          dotData: FlDotData(show: false),
                        ),

                        // Lower bound (for shading)
                        LineChartBarData(
                          spots: lowerSpots,
                          isCurved: true,
                          color: Colors.transparent,
                          aboveBarData: BarAreaData(
                            show: true,
                            color: Colors.blue.withOpacity(0.2),
                          ),
                          dotData: FlDotData(show: false),
                        ),
                      ],
                      extraLinesData: ExtraLinesData(
                        verticalLines: [
                          if (todayIndex >= 0)
                            VerticalLine(
                              x: todayIndex.toDouble(),
                              color: Colors.red,
                              strokeWidth: 2,
                              dashArray: [4, 4],
                            ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                // Legend
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: const [
                    LegendItem(color: Colors.blue, text: "Predicted"),
                    LegendItem(color: Colors.blueAccent, text: "Uncertainty"),
                    LegendItem(color: Colors.red, text: "Today"),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

// Legend widget
class LegendItem extends StatelessWidget {
  final Color color;
  final String text;

  const LegendItem({required this.color, required this.text, super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(width: 20, height: 5, color: color),
        const SizedBox(width: 5),
        Text(text, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}