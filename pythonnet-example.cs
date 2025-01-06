using Python.Runtime;

public class PythonIntegration
{
    public void RunPythonCode()
    {
       // Initialize Python environment
        PythonEngine.Initialize();

        using (Py.GIL()) // Acquire the Global Interpreter Lock
        {
            try
            {
                // Import the Python script
                dynamic movieRecommendations = Py.Import("movie_recommendations");

                // Call the Python function
                dynamic result = movieRecommendations.get_recommended_movies(335984, 30);

                // Convert the result to a C# list
                var recommendedMovies = new List<int>();
                foreach (var movieId in result)
                {
                    recommendedMovies.Add((int)movieId);
                }

                // Display the recommended movies
                Console.WriteLine("Podobne do Blade Runner 2049:");
                foreach (var movie in recommendedMovies)
                {
                    Console.WriteLine(movie);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred: {ex.Message}");
            }
        }

        // Shutdown Python environment
        PythonEngine.Shutdown();
    }
}