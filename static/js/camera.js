let stream = null;
let frontBlob = null;
let backBlob = null;

const video = document.getElementById('camera-feed');
const startBtn = document.getElementById('start-cam-btn');
const captureFrontBtn = document.getElementById('snap-front-btn');
const captureBackBtn = document.getElementById('snap-back-btn');
const frontCanvas = document.getElementById('canvas-front');
const backCanvas = document.getElementById('canvas-back');

startBtn.addEventListener('click', async () => {
  try {
    alert("Tip: Hold the product straight with all label text, MRP, and manufacturing details clearly illuminated.");
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "environment" } 
    });
    video.srcObject = stream;
    video.play();
    startBtn.style.display = 'none';
    captureFrontBtn.disabled = false;
  } catch (err) {
    alert("Webcam access denied or unavailable: " + err.message);
  }
});

function captureFrame(canvas, callback) {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.toBlob(callback, 'image/jpeg', 0.95);
}

captureFrontBtn.addEventListener('click', () => {
  captureFrame(frontCanvas, (blob) => {
    frontBlob = blob;
    document.getElementById('front-status').innerText = "✓ Front Captured";
    captureBackBtn.disabled = false;
  });
});

captureBackBtn.addEventListener('click', () => {
  captureFrame(backCanvas, (blob) => {
    backBlob = blob;
    document.getElementById('back-status').innerText = "✓ Back Captured";
    document.getElementById('submit-camera-btn').disabled = false;
  });
});

document.getElementById('camera-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!frontBlob || !backBlob) {
    alert("Please capture both front and back packaging sides before submission.");
    return;
  }

  const category = document.getElementById('camera-category-select').value;
  const formData = new FormData();
  formData.append('category', category);
  formData.append('front_image', frontBlob, 'front_capture.jpg');
  formData.append('back_image', backBlob, 'back_capture.jpg');

  submitAuditData(formData);
});

async function submitAuditData(formData) {
  const loadingIndicator = document.getElementById('loading-overlay');
  loadingIndicator.style.display = 'block';

  try {
    const res = await fetch('/process-scan', {
      method: 'POST',
      body: formData
    });
    const result = await res.json();
    if (res.ok && result.redirect_url) {
      window.location.href = result.redirect_url;
    } else {
      alert("Inspection failure: " + (result.error || "Unknown error occurred."));
      loadingIndicator.style.display = 'none';
    }
  } catch (err) {
    alert("Network or inference error: " + err.message);
    loadingIndicator.style.display = 'none';
  }
}