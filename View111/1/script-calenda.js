let historyList = [];

function selectMood(mood) {
    // รีเซ็ตการเลือกทั้งหมด
    document.querySelectorAll('.mood-btn').forEach(btn => btn.classList.remove('selected'));
    
    // เลือกปุ่มที่กดและทำให้มันมีสีเหลือง
    const selectedBtn = document.querySelector(`.mood-btn.${mood}`);
    selectedBtn.classList.add('selected');

    // บันทึกการเลือกอารมณ์ในประวัติ
    const date = new Date().toLocaleDateString();
    const moodText = mood === 'happy' ? '😊 ยิ้มกว้าง' :
                     mood === 'smile' ? '😄 ยิ้ม' :
                     mood === 'meh' ? '😐 เฉยๆ' : '😠 โกรธ';
    addToHistory(`${date}: ${moodText}`);
}

function addWeight() {
    const weight = document.getElementById('weight').value;
    const weightDate = document.getElementById('weight-date').value;
    const date = weightDate ? weightDate : new Date().toLocaleDateString();
    addToHistory(`${date}: น้ำหนัก ${weight} kg`);
}

function addTemperature() {
    const temperature = document.getElementById('temperature').value;
    const temperatureDate = document.getElementById('temperature-date').value;
    const date = temperatureDate ? temperatureDate : new Date().toLocaleDateString();
    addToHistory(`${date}: อุณหภูมิ ${temperature} °C`);
}

function saveData() {
    const date = document.getElementById('date').value;
    const percentage = document.getElementById('percentage').value;
    const notes = document.getElementById('notes').value;

    console.log("บันทึกข้อมูล: ");
    console.log("วันที่: " + date);
    console.log("เปอร์เซ็นต์: " + percentage + "%");
    console.log("โน้ต: " + notes);
    
    alert("ข้อมูลถูกบันทึกแล้ว!");
}

function addToHistory(record) {
    historyList.push(record);
    updateHistory();
}

function updateHistory() {
    const historyUl = document.getElementById('historyList');
    historyUl.innerHTML = '';
    historyList.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        historyUl.appendChild(li);
    });
}
