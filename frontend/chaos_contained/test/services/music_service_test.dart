import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';
import 'package:mockito/annotations.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:chaos_contained/services/music_service.dart';
import 'package:chaos_contained/services/api_service.dart';
import 'music_service_test.mocks.dart';

@GenerateMocks([FlutterSecureStorage, ApiService])
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late MusicService musicService;
  late MockFlutterSecureStorage mockStorage;
  late MockApiService mockApiService;

  setUp(() {
    mockStorage = MockFlutterSecureStorage();
    mockApiService = MockApiService();
    musicService = MusicService.forTesting(
      storage: mockStorage,
      api: mockApiService,
    );
    when(mockStorage.read(key: anyNamed('key'))).thenAnswer((_) async => null);
  });

  group('MusicService Provider Connection', () {
    test('connectProvider should get and launch auth URL', () async {
      when(mockApiService.post('/music/connect/', data: {
        'provider': 'spotify'
      })).thenAnswer((_) async => Response(
        data: {'auth_url': 'https://spotify.com/auth'},
        statusCode: 200,
        requestOptions: RequestOptions(path: ''))
      );

      await musicService.connectProvider(MusicProvider.spotify);
      
      verify(mockApiService.post('/music/connect/', data: {
        'provider': 'spotify'
      })).called(1);
      // Note: Can't verify url_launcher as it's not mockable
    });

    test('isConnected should check token storage', () async {
      when(mockStorage.read(key: 'music_spotify_tokens'))
          .thenAnswer((_) async => '{"access":"token"}');

      final result = await musicService.isConnected(MusicProvider.spotify);

      expect(result, true);
      verify(mockStorage.read(key: 'music_spotify_tokens')).called(1);
    });

    test('disconnect should remove stored tokens', () async {
      await musicService.disconnect(MusicProvider.spotify);

      verify(mockStorage.delete(key: 'music_spotify_tokens')).called(1);
    });
  });

  group('MusicService Playback Controls', () {
    setUp(() async {
      // Setup mock for active provider
      when(mockStorage.read(key: 'music_spotify_tokens'))
          .thenAnswer((_) async => '{"access":"token"}');
    });

    test('play should call API endpoint', () async {
      when(mockApiService.post('/music/spotify/play'))
          .thenAnswer((_) async => Response(
                statusCode: 200,
                requestOptions: RequestOptions(path: '')
              ));

      final result = await musicService.play();

      expect(result, true);
      verify(mockApiService.post('/music/spotify/play')).called(1);
    });

    test('pause should call API endpoint', () async {
      when(mockApiService.post('/music/spotify/pause'))
          .thenAnswer((_) async => Response(
                statusCode: 200,
                requestOptions: RequestOptions(path: '')
              ));

      final result = await musicService.pause();

      expect(result, true);
      verify(mockApiService.post('/music/spotify/pause')).called(1);
    });

    test('next should call API endpoint', () async {
      when(mockApiService.post('/music/spotify/next'))
          .thenAnswer((_) async => Response(
                statusCode: 200,
                requestOptions: RequestOptions(path: '')
              ));

      final result = await musicService.next();

      expect(result, true);
      verify(mockApiService.post('/music/spotify/next')).called(1);
    });

    test('previous should call API endpoint', () async {
      when(mockApiService.post('/music/spotify/previous'))
          .thenAnswer((_) async => Response(
                statusCode: 200,
                requestOptions: RequestOptions(path: '')
              ));

      final result = await musicService.previous();

      expect(result, true);
      verify(mockApiService.post('/music/spotify/previous')).called(1);
    });

    test('playback controls should fail gracefully when no provider connected', () async {
      when(mockStorage.read(key: 'music_spotify_tokens'))
          .thenAnswer((_) async => null);

      expect(await musicService.play(), false);
      expect(await musicService.pause(), false);
      expect(await musicService.next(), false);
      expect(await musicService.previous(), false);
    });
  });
}