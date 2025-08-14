---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

1. **Project Context**:
   - This project is a demonstration of using Pydantic for structured output in Python applications.
   - The goal is to showcase how Pydantic can be used to validate and serialize complex data structures.

2. **Coding Guidelines**:
   - Follow PEP 8 style guidelines for Python code.
   - Use type annotations for all function signatures and complex data structures.
   - Write unit tests for all new features and bug fixes.
   - Include docstrings for all public classes and functions.
   - Keep code DRY (Don't Repeat Yourself) by reusing existing functions and classes where applicable.
   - Use Pydantic models to define and validate data structures.
   - Leverage Pydantic's built-in validation features to enforce data integrity.
   - Use Pydantic's serialization capabilities to convert models to and from JSON.

 3. **Tech Stack**  
   - Python 3.11+
   - Pydantic
   - Python Quart (for demonstration purposes)
   - pytest (for testing)
   - docker compose (for containerization)
   - gpt-oss:20b (on local workstation for AI model integration)

 4. **UI**  
   - Use a responsive design framework (Tailwind CSS) for the frontend.
   - Implement a RESTful API using Python Quart to serve the frontend.
   - Ensure the UI is accessible and follows best practices for usability.
   - The UI should be a generative chat interface that allows users to interact with the AI model.

 5. **Run the app**
 - use docker compose to start the application