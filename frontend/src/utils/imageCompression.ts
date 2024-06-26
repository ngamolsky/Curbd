export const compressImage = (image: File) => {
  return new Promise<File>((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(image);
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target?.result as string;
      img.onload = () => {
        const elem = document.createElement("canvas");
        const scaleFactor = 0.7; // Adjust this value to balance size and quality
        elem.width = img.width * scaleFactor;
        elem.height = img.height * scaleFactor;
        const ctx = elem.getContext("2d");
        ctx?.drawImage(img, 0, 0, elem.width, elem.height);
        ctx?.canvas.toBlob(
          (blob) => {
            const file = new File([blob!], image.name, {
              type: "image/jpeg",
              lastModified: Date.now(),
            });

            // Log original and compressed file sizes in MB
            console.log(
              `Original file size: ${(image.size / (1024 * 1024)).toFixed(
                2
              )} MB`
            );
            console.log(
              `Compressed file size: ${(file.size / (1024 * 1024)).toFixed(
                2
              )} MB`
            );
            console.log(
              `Compression ratio: ${((file.size / image.size) * 100).toFixed(
                2
              )}%`
            );

            resolve(file);
          },
          "image/jpeg",
          0.8 // Adjust compression quality (0-1)
        );
      };
      img.onerror = (error) => reject(error);
    };
    reader.onerror = (error) => reject(error);
  });
};
