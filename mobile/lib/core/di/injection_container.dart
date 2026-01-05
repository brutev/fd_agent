import 'package:get_it/get_it.dart';

final sl = GetIt.instance;

Future<void> init() async {
  // Register your dependencies here
  // Example:
  // sl.registerLazySingleton(() => YourRepository());
  // sl.registerFactory(() => YourBloc(sl()));
}
