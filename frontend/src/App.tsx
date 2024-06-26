import { useState, ChangeEvent } from "react";
import { compressImage } from "./utils/imageCompression"; // Assuming you have this utility function
import { OpenAPI, generatePost } from "./client";

const MAX_IMAGE_SIZE = 4 * 1024 * 1024; // 4MB in bytes
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

  const handleImageUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
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
      setThumbnails((prevThumbnails) => [...prevThumbnails, ...newThumbnails]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    const response = await generatePost({
      formData: {
        images: images,
        user_input: userInput,
      },
    });

    console.log(response);
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col items-center justify-start p-4">
      <h1 className="text-3xl sm:text-4xl font-bold mb-6 text-center text-gray-800 dark:text-white">
        Curbd
      </h1>
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
          disabled={isLoading}
          className={`w-full py-3 px-4 rounded-md text-base font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300 ease-in-out transform hover:scale-105 ${
            isLoading
              ? "bg-gray-400 text-gray-700 cursor-not-allowed"
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
    </div>
  );
}

export default App;
