import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:provider/provider.dart';
import 'package:chaos_contained/screens/conversation_history_screen.dart';
import 'package:chaos_contained/services/memory_service.dart';
import 'package:chaos_contained/models/memory.dart';
import 'conversation_history_screen_test.mocks.dart';

void main() {
  late MockMemoryService mockMemoryService;

  setUp(() {
    mockMemoryService = MockMemoryService();
  });

  group('ConversationHistoryScreen Widget Tests', () {
    testWidgets('Shows list of memories', (WidgetTester tester) async {
      // Mock memories
      final memories = [
        Memory(
          id: 1,
          message: 'Recent message',
          role: 'user',
          timestamp: DateTime.now(),
          relevanceScore: 1.0,
          context: {'mood': 'happy'}
        ),
        Memory(
          id: 2,
          message: 'Older message',
          role: 'assistant',
          timestamp: DateTime.now().subtract(const Duration(days: 1)),
          relevanceScore: 0.8,
          context: {'mood': 'neutral'}
        ),
      ];

      when(mockMemoryService.getMemories()).thenAnswer((_) async => memories);

      await tester.pumpWidget(
        MaterialApp(
          home: Provider<MemoryService>.value(
            value: mockMemoryService,
            child: const ConversationHistoryScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify memories are displayed
      expect(find.text('Recent message'), findsOneWidget);
      expect(find.text('Older message'), findsOneWidget);
      // Relative date labels are formatted; exact text may vary.
    });

    testWidgets('Shows loading indicator while fetching memories',
        (WidgetTester tester) async {
      // Mock delayed response
      when(mockMemoryService.getMemories()).thenAnswer((_) async {
        await Future.delayed(const Duration(milliseconds: 500));
        return [];
      });

      await tester.pumpWidget(
        MaterialApp(
          home: Provider<MemoryService>.value(
            value: mockMemoryService,
            child: const ConversationHistoryScreen(),
          ),
        ),
      );
      await tester.pump();

      // Should show loading indicator
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      // Wait for response
      await tester.pumpAndSettle();

      // Loading indicator should be gone
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    testWidgets('Search filters memories by query', (WidgetTester tester) async {
      // Initial list
      when(mockMemoryService.getMemories()).thenAnswer((_) async => [
        Memory(
          id: 1,
          message: 'Recent message',
          role: 'user',
          timestamp: DateTime.now(),
          relevanceScore: 1.0,
          context: const {'mood': 'happy'},
        ),
      ]);
      // Search API returns different results
      when(mockMemoryService.searchMemories(any)).thenAnswer((_) async => MemorySearchResult(memories: [
        Memory(
          id: 2,
          message: 'Search hit message',
          role: 'assistant',
          timestamp: DateTime.now().subtract(const Duration(days: 1)),
          relevanceScore: 0.8,
          context: const {'mood': 'neutral'},
        ),
      ]));

      await tester.pumpWidget(
        MaterialApp(
          home: Provider<MemoryService>.value(
            value: mockMemoryService,
            child: const ConversationHistoryScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Enter a query (>=3 chars triggers search)
      await tester.enterText(find.byType(TextField), 'hit');
      await tester.pumpAndSettle();

      expect(find.text('Search hit message'), findsOneWidget);
    });

    // Deletion UI is not part of the simplified design; skip delete interactions.

    testWidgets('Shows error on memory fetch failure', (WidgetTester tester) async {
      // Mock service failure
      when(mockMemoryService.getMemories())
          .thenThrow(Exception('Failed to fetch memories'));

      await tester.pumpWidget(
        MaterialApp(
          home: Provider<MemoryService>.value(
            value: mockMemoryService,
            child: const ConversationHistoryScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Should show error message
      expect(find.textContaining('Failed to load memories'), findsOneWidget);
    });
  });
}