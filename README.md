# AI Chatbot with Streamlit and LangGraph

A simple yet powerful chatbot application built with Streamlit and LangGraph, leveraging OpenAI's language models for natural conversations.

## Features

- Interactive chat interface using Streamlit
- Stateful conversation management with LangGraph
- Integration with OpenAI's GPT models
- Easy to extend with custom functionality

## Prerequisites

- Python 3.8+
- OpenAI API key

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sommelier
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Running the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

Then open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501).

## How It Works

The application uses:

- **Streamlit** for the web interface
- **LangGraph** for managing the conversation state and flow
- **OpenAI's GPT-3.5-turbo** for generating responses

## Customization

You can modify the behavior by:

1. Adjusting the temperature in `app.py`
2. Changing the model (e.g., to `gpt-4` if you have access)
3. Adding more sophisticated conversation logic in the graph nodes

## License

MIT