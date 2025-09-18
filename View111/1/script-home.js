const images = [
  "images/ป้องกันโรคเบาหวาน.jpg",
  "images/โรคเบาหวานคือ.jpg",
  "images/การวินิจฉัยโรคเบาหวาน.jpg",
  "images/เป้าหมายการดูแล.jpg"
];

let currentIndex = 0;
let autoRotate = true;

function showImage(index) {
  currentIndex = index;
  document.getElementById("mainDisplay").src = images[currentIndex];
  autoRotate = false; // หยุด auto หากผู้ใช้คลิกเลือก
}

// Auto rotate every 9 seconds
setInterval(() => {
  if (autoRotate) {
    currentIndex = (currentIndex + 1) % images.length;
    document.getElementById("mainDisplay").src = images[currentIndex];
  }
}, 9000);
