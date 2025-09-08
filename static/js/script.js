// Initialize Speech Recognition & Synthesis
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = 'en-US';

const askBtn = document.getElementById('ask-btn');
const transcriptP = document.getElementById('transcript');
const answerBox = document.getElementById('answer-box');

askBtn.addEventListener('click', () => {
  transcriptP.textContent = 'Listening...';
  answerBox.textContent = '';
  recognition.start();
});

recognition.onresult = async (event) => {
  const text = event.results[0][0].transcript;
  transcriptP.textContent = `You said: "${text}"`;

  // Only proceed if user asks “what is this”
  if (/what\s+is\s+this/i.test(text)) {
    const resp = await fetch('/describe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text })
    });
    const data = await resp.json();
    answerBox.textContent = data.answer;

    // Speak the answer
    const utter = new SpeechSynthesisUtterance(data.answer);
    utter.lang = 'en-US';
    speechSynthesis.speak(utter);
  } else {
    answerBox.textContent = 'Please ask, “What is this?”';
  }
};

recognition.onerror = (e) => {
  transcriptP.textContent = 'Error in speech recognition: ' + e.error;
};