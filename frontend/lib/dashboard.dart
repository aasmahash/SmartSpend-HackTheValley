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
    final String response = await rootBundle.loadString('assets/forecast.json');
    return jsonDecode(response);
  }

  Future<List<Map<String, dynamic>>> loadSpendingData() async {
    final String response = await rootBundle.loadString('spending_by_month.json');
    final data = jsonDecode(response);

    final colors = [
      Colors.teal,
      Colors.blue,
      Colors.purple,
      Colors.pink,
      Colors.orange,
      Colors.amber,
      Colors.red,
    ];

    int colorIndex = 0;

    return (data as List).map<Map<String, dynamic>>((month) {
      final item = {
        "label": month["month"],
        "value": month["total_spending"],
        "color": colors[colorIndex % colors.length],
      };
      colorIndex++;
      return item;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text("Dashboard"),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        elevation: 4,
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Text(
                "📊 Spending & Forecast Overview",
                style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.indigo),
              ),
              const SizedBox(height: 30),

              // Forecast Chart Section
              FutureBuilder<Map<String, dynamic>>(
                future: loadForecastData(),
                builder: (context, snapshot) {
                  if (!snapshot.hasData) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  final data = snapshot.data!["forecast"];
                  final List<String> dates = List<String>.from(data["dates"]);
                  final List<double> predicted =
                      List<double>.from(data["predicted"].map((v) => v.toDouble()));
                  final List<double> lower =
                      List<double>.from(data["lower_bound"].map((v) => v.toDouble()));
                  final List<double> upper =
                      List<double>.from(data["upper_bound"].map((v) => v.toDouble()));

                  final List<FlSpot> predictedSpots = List.generate(
                      predicted.length, (i) => FlSpot(i.toDouble(), predicted[i]));
                  final List<FlSpot> lowerSpots =
                      List.generate(lower.length, (i) => FlSpot(i.toDouble(), lower[i]));
                  final List<FlSpot> upperSpots =
                      List.generate(upper.length, (i) => FlSpot(i.toDouble(), upper[i]));

                  final minY = [...lower, ...predicted, ...upper]
                      .reduce((a, b) => a < b ? a : b);
                  final maxY = [...lower, ...predicted, ...upper]
                      .reduce((a, b) => a > b ? a : b);

                  final todayIndex = dates.indexWhere((d) =>
                      DateTime.parse(d).year == DateTime.now().year &&
                      DateTime.parse(d).day == DateTime.now().day &&
                      DateTime.parse(d).month == DateTime.now().month);

                  return Container(
                    width: 800,
                    height: 400,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                            color: Colors.black12,
                            blurRadius: 8,
                            offset: const Offset(0, 4))
                      ],
                    ),
                    child: Column(
                      children: [
                        const Text(
                          "Spending Forecast",
                          style: TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 18),
                        ),
                        const SizedBox(height: 20),
                        Expanded(
                          child: LineChart(
                            LineChartData(
                              minY: minY - 50,
                              maxY: maxY + 50,
                              gridData: FlGridData(show: true),
                              titlesData: FlTitlesData(
                                bottomTitles: AxisTitles(
                                  sideTitles: SideTitles(
                                    showTitles: true,
                                    interval:
                                        (dates.length / 5).floorToDouble(),
                                    getTitlesWidget: (value, meta) {
                                      int index = value.toInt();
                                      if (index < 0 || index >= dates.length) {
                                        return const SizedBox.shrink();
                                      }
                                      return Text(
                                        dates[index],
                                        style: const TextStyle(fontSize: 10),
                                      );
                                    },
                                  ),
                                ),
                                leftTitles: AxisTitles(
                                  sideTitles: SideTitles(
                                      showTitles: true, reservedSize: 50),
                                ),
                              ),
                              borderData: FlBorderData(show: true),
                              lineBarsData: [
                                LineChartBarData(
                                  spots: predictedSpots,
                                  isCurved: true,
                                  color: Colors.blue,
                                  barWidth: 3,
                                  dotData: FlDotData(show: false),
                                  dashArray: [5, 5],
                                ),
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
                        const SizedBox(height: 10),
                        const Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            LegendItem(color: Colors.blue, text: "Predicted"),
                            LegendItem(color: Colors.blueAccent, text: "Range"),
                            LegendItem(color: Colors.red, text: "Today"),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),

              const SizedBox(height: 50),

              // Spending Chart Section
              FutureBuilder<List<Map<String, dynamic>>>(
                future: loadSpendingData(),
                builder: (context, snapshot) {
                  if (!snapshot.hasData) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  final spendingData = snapshot.data!;
                  final totalSpending = (spendingData.fold(
                    0.0,
                    (sum, item) => sum + item["value"],
                  ) * 100).round() / 100;

                  return Column(
                    children: [
                      const Text(
                        "Monthly Spending Breakdown",
                        style: TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 18),
                      ),
                      const SizedBox(height: 20),
                      Container(
                        width: 800,
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                                color: Colors.black12,
                                blurRadius: 8,
                                offset: const Offset(0, 4))
                          ],
                        ),
                        child: SpendingPieChart(
                          spendingData: spendingData,
                          totalSpending: totalSpending,
                        ),
                      ),
                      const SizedBox(height: 30),
                      _buildSpendingTable(spendingData, totalSpending),
                    ],
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSpendingTable(
      List<Map<String, dynamic>> spendingData, double totalSpending) {
    return Container(
      width: 800,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
              color: Colors.black12, blurRadius: 8, offset: const Offset(0, 4))
        ],
      ),
      child: Column(
        children: [
          const Text("Spending Table",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const Divider(),
          ...spendingData.map((item) {
            final percentage =
                ((item["value"] / totalSpending) * 100).toStringAsFixed(1);
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Row(
                children: [
                  Expanded(
                    child: Row(
                      children: [
                        CircleAvatar(radius: 5, backgroundColor: item["color"]),
                        const SizedBox(width: 8),
                        Text(item["label"]),
                      ],
                    ),
                  ),
                  Expanded(
                      child: Center(
                          child: Text("\$${item["value"]}",
                              style:
                                  const TextStyle(fontWeight: FontWeight.bold)))),
                  Expanded(
                      child: Center(
                          child: Text("$percentage%",
                              style: const TextStyle(
                                  fontWeight: FontWeight.w500)))),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }
}

// Pie chart widget
class SpendingPieChart extends StatefulWidget {
  final List<Map<String, dynamic>> spendingData;
  final double totalSpending;

  const SpendingPieChart({
    super.key,
    required this.spendingData,
    required this.totalSpending,
  });

  @override
  State<SpendingPieChart> createState() => _SpendingPieChartState();
}

class _SpendingPieChartState extends State<SpendingPieChart> {
  int? touchedIndex;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Text("Spendings Overview (Tap to view details)",
            style: TextStyle(color: Colors.black54)),
        const SizedBox(height: 20),
        SizedBox(
          height: 220,
          child: Stack(
            alignment: Alignment.center,
            children: [
              PieChart(
                PieChartData(
                  pieTouchData: PieTouchData(
                    touchCallback: (event, pieTouchResponse) {
                      setState(() {
                        if (!event.isInterestedForInteractions ||
                            pieTouchResponse?.touchedSection == null) {
                          touchedIndex = null;
                          return;
                        }
                        touchedIndex = pieTouchResponse!
                            .touchedSection!.touchedSectionIndex;
                      });
                    },
                  ),
                  sections: List.generate(widget.spendingData.length, (i) {
                    final item = widget.spendingData[i];
                    final isTouched = (i == touchedIndex);
                    return PieChartSectionData(
                      color: item["color"],
                      value: item["value"],
                      radius: isTouched ? 110 : 100,
                      title: isTouched
                          ? "${item["label"]}\n\$${item["value"]}"
                          : "",
                      titleStyle: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Colors.white),
                    );
                  }),
                  centerSpaceRadius: 80,
                ),
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text("Total Spending",
                      style: TextStyle(fontSize: 14, color: Colors.black54)),
                  Text("\$${widget.totalSpending}",
                      style: const TextStyle(
                          fontSize: 22, fontWeight: FontWeight.bold)),
                ],
              ),
            ],
          ),
        ),
      ],
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