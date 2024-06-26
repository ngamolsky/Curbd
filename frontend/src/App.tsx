import { useState, ChangeEvent } from "react";
import { compressImage } from "./utils/imageCompression";
import { OpenAPI, generatePost } from "./client";

const MAX_IMAGE_SIZE = 1 * 1024 * 1024; // 1MB in bytes
const BASE_API_URL =
  import.meta.env.DEV === true
    ? "http://localhost:8000"
    : import.meta.env.VITE_BACKEND_URL;

OpenAPI.BASE = BASE_API_URL;
OpenAPI.HEADERS = {
  "x-api-key": import.meta.env.VITE_API_KEY,
};

function App() {
  const [images, setImages] = useState<File[]>([]);
  const [userInput, setUserInput] = useState("");
  const [thumbnails, setThumbnails] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [generatedPost, setGeneratedPost] = useState<{
    title: string;
    description: string;
    hashtags: string[];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleImageUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      try {
        const processedImages = await Promise.all(
          Array.from(e.target.files).map(async (file) => {
            if (file.size > MAX_IMAGE_SIZE) {
              return await compressImage(file);
            }
            return file;
          })
        );
        setImages((prevImages) => [...prevImages, ...processedImages]);

        // Generate thumbnails
        const newThumbnails = await Promise.all(
          processedImages.map((file) => URL.createObjectURL(file))
        );
        setThumbnails((prevThumbnails) => [
          ...prevThumbnails,
          ...newThumbnails,
        ]);
      } catch (err) {
        setError("Error processing images. Please try again.");
        console.error("Error processing images:", err);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const response = await generatePost({
        formData: {
          images: images,
          user_input: userInput,
        },
      });

      const post = response.post;

      setGeneratedPost({
        title: post.title,
        description: post.description,
        hashtags: post.hashtags,
      });
    } catch (err) {
      setError("Error generating post. Please try again.");
      console.error("Error generating post:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setImages([]);
    setUserInput("");
    setThumbnails([]);
    setGeneratedPost(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col items-center justify-start p-4">
      <h1 className="text-3xl sm:text-4xl font-bold mb-6 text-center text-gray-800 dark:text-white">
        Curbd
      </h1>

      {!generatedPost ? (
        <form
          onSubmit={handleSubmit}
          className="bg-white dark:bg-gray-800 p-4 sm:p-8 rounded-lg shadow-md w-full max-w-md"
        >
          <div className="mb-4 sm:mb-6">
            <label
              htmlFor="images"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Upload Images
            </label>
            <input
              type="file"
              id="images"
              accept="image/*"
              multiple
              onChange={handleImageUpload}
              className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          {thumbnails.length > 0 && (
            <div className="mb-4 sm:mb-6">
              <p className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Uploaded Images:
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {thumbnails.map((thumbnail, index) => (
                  <img
                    key={index}
                    src={thumbnail}
                    alt={`Thumbnail ${index + 1}`}
                    className="w-20 h-20 sm:w-24 sm:h-24 object-cover rounded-md"
                  />
                ))}
              </div>
            </div>
          )}

          <div className="mb-4 sm:mb-6">
            <label
              htmlFor="userInput"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Modify Post
            </label>
            <textarea
              id="userInput"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              rows={4}
            ></textarea>
          </div>

          <button
            type="submit"
            disabled={isLoading || images.length === 0}
            className={`w-full py-3 px-4 rounded-md text-base font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300 ease-in-out ${
              isLoading || images.length === 0
                ? "bg-blue-300 text-white cursor-not-allowed"
                : "bg-blue-500 text-white hover:bg-blue-600"
            }`}
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Generating...
              </div>
            ) : (
              "Generate Post"
            )}
          </button>
        </form>
      ) : (
        <div className="bg-white dark:bg-gray-800 p-4 sm:p-8 rounded-lg shadow-md w-full max-w-md">
          <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">
            {generatedPost.title}
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            {generatedPost.description}
          </p>
          <div className="flex flex-wrap gap-2 mb-4">
            {generatedPost.hashtags.map((hashtag, index) => (
              <span
                key={index}
                className="bg-blue-100 text-blue-800 text-sm font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-blue-900 dark:text-blue-300"
              >
                {hashtag.startsWith("#") ? hashtag : `#${hashtag}`}
              </span>
            ))}
          </div>
          <button
            onClick={handleReset}
            className="w-full py-3 px-4 rounded-md text-base font-medium bg-gray-500 text-white hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 transition duration-300 ease-in-out"
          >
            Reset
          </button>
        </div>
      )}
      {error && (
        <div
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative my-4"
          role="alert"
        >
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}
    </div>
  );
}

export default App;
