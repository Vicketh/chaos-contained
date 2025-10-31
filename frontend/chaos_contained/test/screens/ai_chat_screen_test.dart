import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:chaos_contained/screens/ai_chat_screen.dart';
import 'package:mockito/mockito.dart';

void main() {
  group('AIChatScreen Widget Tests', () {
    testWidgets('Shows chat input and sends messages', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(home: AIChatScreen()));
      await tester.pump();

      // Verify chat input exists
      expect(find.byType(TextField), findsOneWidget);
      expect(find.byIcon(Icons.send), findsOneWidget);

      // Enter text and send message
      await tester.enterText(find.byType(TextField), 'Test message');
      await tester.tap(find.byIcon(Icons.send));
      await tester.pump();

      // Message should appear in chat
      expect(find.text('Test message'), findsOneWidget);
      // Loading indicator should appear
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('Shows loading indicator while waiting for response',
        (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(home: AIChatScreen()));

      // Send message
      await tester.enterText(find.byType(TextField), 'Test message');
      await tester.tap(find.byIcon(Icons.send));
      await tester.pump();

      // Should show loading indicator
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      // Do not wait for network; just verify loader presence
    });
  });
}