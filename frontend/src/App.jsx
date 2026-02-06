import { BrowserRouter, Routes, Route } from "react-router-dom";
import Upload from "./pages/Upload";
import Jobs from "./pages/Jobs";
import Navbar from "./components/Navbar";

function App() {
  return (
    <BrowserRouter>
      <div className="container">
        <Navbar />
        <Routes>
          <Route path="/" element={<Upload />} />
          <Route path="/jobs" element={<Jobs />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
