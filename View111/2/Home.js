import React, { useEffect, useState } from 'react';
import './Home.css'; // สร้างไฟล์ CSS แยก
import slide1 from './images/slide1.png';
import slide2 from './images/slide2.png';
import slide3 from '/images/slide3.png';
import info1 from './images/info1.png';
import info2 from '.images/info2.png';
import info3 from './images/info3.png';

function Home() {
  const slides = [slide1, slide2, slide3];
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrent((prev) => (prev + 1) % slides.length);
    }, 10000);
    return () => clearInterval(interval);
  }, [slides.length]);

  return (
    <div>
      <header>
        <div className="left">
          <img src="https://via.placeholder.com/40x40" className="logo" alt="logo" />
          <h2>SugarFree</h2>
        </div>
        <h3>Welcome, Mr.Health</h3>
        <div className="search-bar">
          <input type="text" placeholder="ค้นหา..." />
        </div>
      </header>

      <nav>
        <i className="fas fa-home"></i>
        <i className="fas fa-calendar-alt"></i>
        <i className="fas fa-user"></i>
        <i className="fas fa-bars"></i>
      </nav>

      <div className="container">
        <div className="main-content">
          <img src={slides[current]} alt="slide" />
        </div>
        <div className="side-content">
          <img src={info1} alt="info1" />
          <img src={info2} alt="info2" />
          <img src={info3} alt="info3" />
        </div>
      </div>

      <div className="chat-btn">
        <img src="https://cdn-icons-png.flaticon.com/512/4712/4712100.png" alt="chat" />
      </div>
    </div>
  );
}

export default Home;
