// API Configuration
const API_BASE_URL = window.location.origin + '/api';

// State
let state = {
  currentStep: 1,
  referenceImage: null,
  videoSource: null,
  videoType: "file",
  processingMode: "balanced",
  imageValidated: false,
  videoValidated: false,
};

const steps = document.querySelectorAll(".step");
const stepContents = document.querySelectorAll(".step-content");
const imageUploadArea = document.getElementById("imageUploadArea");
const imageInput = document.getElementById("imageInput");
const imagePreview = document.getElementById("imagePreview");
const imagePreviewImg = document.getElementById("imagePreviewImg");
const removeImageBtn = document.getElementById("removeImage");
const validateImageBtn = document.getElementById("validateImageBtn");
const imageValidation = document.getElementById("imageValidation");
const videoSourceRadios = document.querySelectorAll('input[name="videoSource"]');
const videoFileSection = document.getElementById("videoFileSection");
const videoUrlSection = document.getElementById("videoUrlSection");
const videoUploadArea = document.getElementById("videoUploadArea");
const videoInput = document.getElementById("videoInput");
const videoPreview = document.getElementById("videoPreview");
const videoPreviewVideo = document.getElementById("videoPreviewVideo");
const removeVideoBtn = document.getElementById("removeVideo");
const videoUrlInput = document.getElementById("videoUrlInput");
const validateVideoBtn = document.getElementById("validateVideoBtn");
const videoValidation = document.getElementById("videoValidation");
const backToStep1Btn = document.getElementById("backToStep1");
const processingModeRadios = document.querySelectorAll('input[name="processingMode"]');
const backToStep2Btn = document.getElementById("backToStep2");
const startRecognitionBtn = document.getElementById("startRecognitionBtn");
const processingSection = document.getElementById("processingSection");
const resultsSection = document.getElementById("resultsSection");
const errorSection = document.getElementById("errorSection");
const progressFill = document.getElementById("progressFill");
const progressText = document.getElementById("progressText");
const resultsDescription = document.getElementById("resultsDescription");
const matchesList = document.getElementById("matchesList");
const errorMessage = document.getElementById("errorMessage");
const startNewSearchBtn = document.getElementById("startNewSearch");
const retryBtn = document.getElementById("retryBtn");


function updateStepUI(stepNumber) {
    steps.forEach((step, index) => {
        const num = index + 1;
        step.classList.remove("active", "completed");
        if (num === stepNumber) {
            step.classList.add("active");
        } else if (num < stepNumber) {
            step.classList.add("completed");
        }
    });
    stepContents.forEach((content, index) => {
        content.classList.remove("active");
        if (index + 1 === stepNumber) {
            content.classList.add("active");
        }
    });
    state.currentStep = stepNumber;
}

function showValidationMessage(element, message, type) {
    element.textContent = message;
    element.className = `validation-message ${type}`;
    element.classList.remove("hidden");
}

function hideValidationMessage(element) {
    element.classList.add("hidden");
}

imageUploadArea.addEventListener("click", () => imageInput.click());
imageUploadArea.addEventListener("dragover", (e) => { e.preventDefault(); imageUploadArea.classList.add("dragover"); });
imageUploadArea.addEventListener("dragleave", () => { imageUploadArea.classList.remove("dragover"); });
imageUploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    imageUploadArea.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
        handleImageUpload(file);
    }
});
imageInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
        handleImageUpload(file);
    }
});

function handleImageUpload(file) {
    state.referenceImage = file;
    state.imageValidated = false; // <-- Se resetea al cambiar la imagen
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreviewImg.src = e.target.result;
        imageUploadArea.classList.add("hidden");
        imagePreview.classList.remove("hidden");
        validateImageBtn.disabled = false;
        hideValidationMessage(imageValidation);
    };
    reader.readAsDataURL(file);
}

removeImageBtn.addEventListener("click", () => {
    state.referenceImage = null;
    state.imageValidated = false;
    imageInput.value = "";
    imagePreview.classList.add("hidden");
    imageUploadArea.classList.remove("hidden");
    validateImageBtn.disabled = true;
    hideValidationMessage(imageValidation);
});


validateImageBtn.addEventListener("click", async () => {
    if (!state.referenceImage) return;

    validateImageBtn.disabled = true;
    validateImageBtn.textContent = "Validating...";
    hideValidationMessage(imageValidation);

    try {
        const formData = new FormData();
        formData.append("file", state.referenceImage);

        const response = await fetch(`${API_BASE_URL}/upload-image`, {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            state.imageValidated = true;
            showValidationMessage(imageValidation, data.message, "success");
            setTimeout(() => updateStepUI(2), 1000);
        } else {
            state.imageValidated = false;
            showValidationMessage(imageValidation, data.detail, "error");
        }
    } catch (error) {
        state.imageValidated = false;
        showValidationMessage(imageValidation, "Error connecting to server.", "error");
    } finally {
        validateImageBtn.disabled = false;
        validateImageBtn.textContent = "Validate Image";
    }
});


videoSourceRadios.forEach((radio) => {
    radio.addEventListener("change", (e) => {
        state.videoType = e.target.value;
        state.videoSource = null;
        state.videoValidated = false;
        hideValidationMessage(videoValidation);
        if (e.target.value === "file") {
            videoFileSection.classList.remove("hidden");
            videoUrlSection.classList.add("hidden");
        } else {
            videoFileSection.classList.add("hidden");
            videoUrlSection.classList.remove("hidden");
        }
        validateVideoBtn.disabled = true;
    });
});

videoUploadArea.addEventListener("click", () => videoInput.click());

videoInput.addEventListener("change", (e) => { const file = e.target.files[0]; if (file) { handleVideoUpload(file); } });

function handleVideoUpload(file) {
    state.videoSource = file;
    state.videoValidated = false;
    const reader = new FileReader();
    reader.onload = (e) => {
        videoPreviewVideo.src = e.target.result;
        videoUploadArea.classList.add("hidden");
        videoPreview.classList.remove("hidden");
        validateVideoBtn.disabled = false;
        hideValidationMessage(videoValidation);
    };
    reader.readAsDataURL(file);
}

removeVideoBtn.addEventListener("click", () => {
    state.videoSource = null;
    state.videoValidated = false;
    videoInput.value = "";
    videoPreview.classList.add("hidden");
    videoUploadArea.classList.remove("hidden");
    validateVideoBtn.disabled = true;
    hideValidationMessage(videoValidation);
});

videoUrlInput.addEventListener("input", (e) => {
    const url = e.target.value.trim();
    validateVideoBtn.disabled = !url;
    state.videoSource = url;
    state.videoValidated = false;
});


validateVideoBtn.addEventListener("click", async () => {
    const source = (state.videoType === 'file') ? state.videoSource : videoUrlInput.value.trim();
    if (!source) return;

    validateVideoBtn.disabled = true;
    validateVideoBtn.textContent = "Validating...";
    hideValidationMessage(videoValidation);

    try {
        const formData = new FormData();
        if (state.videoType === "url") {
            formData.append("source", source);
        } else {
            formData.append("file", source);
        }

        const response = await fetch(`${API_BASE_URL}/validate-video`, {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            state.videoValidated = true;
            showValidationMessage(videoValidation, data.message, "success");
            setTimeout(() => updateStepUI(3), 1000);
        } else {
            state.videoValidated = false;
            showValidationMessage(videoValidation, data.detail, "error");
        }
    } catch (error) {
        state.videoValidated = false;
        showValidationMessage(videoValidation, "Error connecting to server.", "error");
    } finally {
        validateVideoBtn.disabled = false;
        validateVideoBtn.textContent = "Validate Video";
    }
});

backToStep1Btn.addEventListener("click", () => updateStepUI(1));
backToStep2Btn.addEventListener("click", () => updateStepUI(2));

startRecognitionBtn.addEventListener("click", async () => {
    if (!state.imageValidated) {
        alert("Please validate the reference image first (Step 1)");
        updateStepUI(1);
        return;
    }
    if (!state.videoValidated) {
        alert("Please validate the video source first (Step 2)");
        updateStepUI(2);
        return;
    }

    updateStepUI(4);
    processingSection.classList.remove("hidden");
    resultsSection.classList.add("hidden");
    errorSection.classList.add("hidden");
    progressFill.style.width = "100%";
    progressText.textContent = "Processing... this may take a while.";

    try {
        const formData = new FormData();
        formData.append("reference_image", state.referenceImage);
        const mode = state.processingMode === "high-precision" ? "precision" : "balanced";
        formData.append("mode", mode);

        if (state.videoType === "url") {
            formData.append("video_url", state.videoSource);
        } else {
            formData.append("video_file", state.videoSource);
        }

        const response = await fetch(`${API_BASE_URL}/recognize`, {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            showResults(data);
        } else {
            showError(data.detail || "Recognition failed");
        }
    } catch (error) {
        showError("Error connecting to server: " + error.message);
    }
});


function showResults(data) {
    processingSection.classList.add("hidden");
    resultsSection.classList.remove("hidden");
    const matchCount = data.matches ? data.matches.length : 0;
    resultsDescription.textContent = `Found ${matchCount} match${matchCount !== 1 ? "es" : ""} in the video.`;
    matchesList.innerHTML = "";
    if (matchCount > 0) {
        data.matches.forEach((match) => {
            const matchItem = document.createElement("div");
            matchItem.className = "match-item";
            matchItem.innerHTML = `<div><div class="match-time">Face detected at ${match.timestamp}</div></div>`;
            matchesList.appendChild(matchItem);
        });
    } else {
        matchesList.innerHTML = '<p class="no-matches">No matches found in the video.</p>';
    }
}

function showError(message) {
    processingSection.classList.add("hidden");
    errorSection.classList.remove("hidden");
    errorMessage.textContent = message;
}

startNewSearchBtn.addEventListener("click", () => {
    state = { currentStep: 1, referenceImage: null, videoSource: null, videoType: "file", processingMode: "balanced", imageValidated: false, videoValidated: false, };
    imageInput.value = "";
    videoInput.value = "";
    videoUrlInput.value = "";
    imagePreview.classList.add("hidden");
    videoPreview.classList.add("hidden");
    imageUploadArea.classList.remove("hidden");
    videoUploadArea.classList.remove("hidden");
    validateImageBtn.disabled = true;
    validateVideoBtn.disabled = true;
    hideValidationMessage(imageValidation);
    hideValidationMessage(videoValidation);
    document.querySelector('input[name="videoSource"][value="file"]').checked = true;
    document.querySelector('input[name="processingMode"][value="balanced"]').checked = true;
    videoFileSection.classList.remove("hidden");
    videoUrlSection.classList.add("hidden");
    updateStepUI(1);
});

retryBtn.addEventListener("click", () => { updateStepUI(3); });
updateStepUI(1);