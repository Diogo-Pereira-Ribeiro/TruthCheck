import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  return <main style={{maxWidth: 760, margin: "80px auto", padding: 24, fontFamily: "Arial, sans-serif"}}>
    <h1>TruthCheck</h1>
    <p>Sistema distribuído de análise da credibilidade de notícias.</p>
    <p>Etapa 1: infraestrutura inicial.</p>
  </main>;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode><App /></React.StrictMode>
);
