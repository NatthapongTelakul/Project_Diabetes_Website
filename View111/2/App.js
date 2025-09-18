// src/App.js
import React from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Sign from './Sign';  // นำเข้า Sign.js

function Home() {
  return (
    <div className="App">
      <div className="circle">
        <div className="content">
          <h2 className="en">SugarFree</h2>
          <h1 className="en">WELCOME</h1>
          <p className="th subtitle">
            ตรวจเช็คความเสี่ยงโรคเบาหวานของคุณได้ง่าย ๆ ที่นี่!
          </p>
          <p className="th description">
            ระบบของเราช่วยประเมินความเสี่ยงของโรคเบาหวานผ่านข้อมูลสุขภาพ พร้อมคำแนะนำเพื่อดูแลตัวเอง
          </p>
          <Link to="/sign" className="th start-button">Let's start.</Link>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/sign" element={<Sign />} />
      </Routes>
    </Router>
  );
}

export default App;
