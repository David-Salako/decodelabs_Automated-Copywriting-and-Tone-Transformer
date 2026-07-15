# Automated Copywriting & Tone Transformer

This project was built as part of my Generative AI Industrial Training at DecodeLabs.

## Overview

The Automated Copywriting & Tone Transformer is a tool that uses Google's Gemini AI to turn a simple product description into ready-to-use marketing content.

Instead of writing separate posts for different social media platforms, the tool automatically creates content tailored for platforms such as:

- LinkedIn
- Instagram
- Email
- Twitter/X

For example, if you describe a pair of running shoes, the tool can instantly generate an engaging Instagram caption, a professional LinkedIn post, or a promotional email.

## Features

- Generates marketing copy using AI.
- Creates content for multiple platforms.
- Lets users choose the writing style or tone, such as:
  - Professional
  - Friendly
  - Witty
  - Urgent
- Can generate content for one product or multiple products at once.
- Produces structured and easy-to-read results.

## Requirements

Before running the project, you'll need:

- Python 3.10 or later
- A Gemini API key from Google AI Studio

## Setup

1. Download or clone this project.
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file and add your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

## Running the Project

Start the application by running:

```bash
python main.py
```

The program will ask you a few simple questions, such as:

- Product name
- Product description
- Preferred writing style
- Platform you want the content for

After answering, the AI generates marketing content in seconds.

## Example

### Input

**Product Name:** Nova Sneakers

**Description:** Lightweight running shoes with carbon-fiber soles.

**Tone:** Witty

**Platform:** Instagram

### Output

**Headline**

Your Feet Called. They Want Nova Sneakers.

**Caption**

Meet the sneaker that makes running feel like cheating. Carbon-fiber soles, feather-light comfort, and performance you'll love.

**Call to Action**

Shop the Nova Sneakers today.

## Batch Processing

The project can also process multiple products at once using a CSV file.

Instead of generating content one product at a time, it automatically creates marketing copy for every product in the file.

## Project Files

- **main.py** – Runs the application.
- **gemini_client.py** – Connects the project to Google's Gemini AI.
- **prompt_templates.py** – Defines how the AI should write for different platforms.
- **batch_runner.py** – Processes multiple products at once.
- **requirements.txt** – Lists the required Python packages.
- **README.md** – Project documentation.

## Technologies Used

- Python
- Google Gemini API
- JSON
- CSV

## Future Improvements

Possible enhancements include:

- Supporting more social media platforms.
- Allowing users to set character limits.
- Adding more writing styles.
- Building a web interface so users can use the tool without the command line.

## Author

**David Salako**
