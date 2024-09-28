package main

import (
	"archive/zip"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/schollz/progressbar/v3"
)

// ExtractFile extracts a single file from the zip archive
func ExtractFile(zipFilePath string, file *zip.File, tag string, extractTo string, wg *sync.WaitGroup, bar *progressbar.ProgressBar) {
	defer wg.Done()

	// Create a subfolder based on the file's name (excluding the extension)
	subfolderName := strings.TrimSuffix(file.Name, filepath.Ext(file.Name))
	subfolderPath := filepath.Join(extractTo, subfolderName)
	err := os.MkdirAll(subfolderPath, os.ModePerm)
	if err != nil {
		log.Printf("Error creating directory %s: %v", subfolderPath, err)
		return
	}

	// Open the file inside the zip archive
	rc, err := file.Open()
	if err != nil {
		log.Printf("Error opening file %s: %v", file.Name, err)
		return
	}
	defer rc.Close()

	// Determine the new file path
	fileExtension := filepath.Ext(file.Name)
	newFileName := fmt.Sprintf("%s%s", tag, fileExtension)
	newFilePath := filepath.Join(subfolderPath, newFileName)

	// Create the new file
	newFile, err := os.Create(newFilePath)
	if err != nil {
		log.Printf("Error creating file %s: %v", newFilePath, err)
		return
	}
	defer newFile.Close()

	// Copy the contents to the new file
	_, err = io.Copy(newFile, rc)
	if err != nil {
		log.Printf("Error writing to file %s: %v", newFilePath, err)
		return
	}

	bar.Add(1)
}

// ListAndExtractZipContents lists and extracts the contents of the zip file
func ListAndExtractZipContents(tag string, zipFilePath string, extractTo string) {
	r, err := zip.OpenReader(zipFilePath)
	if err != nil {
		log.Fatalf("Error opening zip file %s: %v", zipFilePath, err)
	}
	defer r.Close()

	var wg sync.WaitGroup
  bar := progressbar.NewOptions64(int64(len(r.File)),
	progressbar.OptionSetDescription("Extracting files..."),
	progressbar.OptionSetWriter(os.Stderr),
	progressbar.OptionSetWidth(100),
	progressbar.OptionThrottle(65*time.Millisecond),
	progressbar.OptionShowCount(),
	progressbar.OptionShowIts(),
	progressbar.OptionSpinnerType(14),
	progressbar.OptionFullWidth(),
	progressbar.OptionSetRenderBlankState(true),
	progressbar.OptionSetItsString("files"),
	progressbar.OptionOnCompletion(func() {
      fmt.Fprint(os.Stderr, "\n")
	}))

	for _, file := range r.File {
		if !file.FileInfo().IsDir() {
			wg.Add(1)
			go ExtractFile(zipFilePath, file, tag, extractTo, &wg, bar)
		}
	}

	wg.Wait()
  bar.Finish()
	fmt.Printf("\nAll files extracted to %s\n", extractTo)
}

func main() {
  fmt.Println("MIRP: Minecraft Resource Pack Indexer")

	tag := flag.String("tag", "", "Tag to rename the extracted files to")
	zipFilePath := flag.String("zip_file_path", "", "Path to the zip file to be processed")
	extractTo := flag.String("extract_to", "", "Directory to extract the contents to")

	flag.Parse()

	if *tag == "" || *zipFilePath == "" || *extractTo == "" {
		log.Fatal("All arguments (tag, zip_file_path, extract_to) are required")
	}

	ListAndExtractZipContents(*tag, *zipFilePath, *extractTo)
}
