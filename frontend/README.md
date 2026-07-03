# Frontend Structure and Flow

This frontend is built using **Angular 17** and styled with **Tailwind CSS**. It is a Single Page Application (SPA) designed to communicate with our FastAPI backend.

## 📂 Directory Structure

```text
frontend/
├── src/
│   ├── app/
│   │   ├── components/      # UI Building Blocks
│   │   │   ├── login/       # Login and Registration forms
│   │   │   ├── layout/      # Navbar, Sidebar, and Page Wrappers
│   │   │   ├── chat/        # Chat interface for interacting with the AI
│   │   │   └── upload/      # Drag-and-drop document upload interface
│   │   ├── services/        # Logic for making HTTP requests to the backend
│   │   │   ├── auth.service.ts  # Handles JWT tokens and login requests
│   │   │   ├── chat.service.ts  # Handles sending/receiving messages to the LLM
│   │   │   └── document.service.ts # Handles file uploads and fetching document lists
│   │   ├── guards/          # Route Protection
│   │   │   └── auth.guard.ts # Prevents unauthenticated users from seeing private pages
│   │   ├── app.routes.ts    # Application routing definitions
│   │   └── app.component.ts # The root component of the Angular application
│   ├── index.html           # The main HTML file loaded by the browser
│   ├── main.ts              # The entry point that boots up the Angular app
│   └── styles.css           # Global CSS and Tailwind directives
├── tailwind.config.js       # Tailwind CSS configuration and theming
└── package.json             # NPM dependencies and scripts
```

## 🔄 The Flow of the Frontend

The frontend acts as the Presentation Layer. It does not perform sensitive logic (like hashing passwords) but instead coordinates UI updates based on data retrieved from the backend API.

### 1. Bootstrapping and Routing (`main.ts` -> `app.routes.ts`)
When a user visits the website, `index.html` loads the Angular Javascript bundle (`main.ts`). Angular checks the URL and uses `app.routes.ts` to decide which Component to display. 

### 2. Route Protection (`auth.guard.ts`)
If the user tries to access `/chat` or `/upload`, the `AuthGuard` intercepts the routing event. It checks `localStorage` to see if a valid JWT token exists. 
- If **yes**, it allows the user to proceed.
- If **no**, it redirects the user to the `/login` page.

### 3. User Interaction (Components)
A user interacts with a component (e.g., clicking the "Upload" button inside the `upload.component.ts`). The component captures the file from the HTML input.

### 4. API Communication (Services)
The Component passes the file to the `DocumentService`. 
Services are singleton classes responsible for external communication. The service uses Angular's `HttpClient` to construct an HTTP request (e.g., `POST /api/v1/documents/upload`). 
Crucially, Angular uses an **HTTP Interceptor** to automatically attach the JWT token from `localStorage` to the `Authorization: Bearer <token>` header of every outgoing request.

### 5. Backend Processing & UI Update
The backend processes the request and returns a JSON response. 
The Service receives the JSON, parses it, and passes it back to the Component. 
The Component updates its internal state (variables), which triggers Angular's change detection to automatically update the HTML view (e.g., showing a green "Upload Successful" banner or updating the chat window with the AI's response).
