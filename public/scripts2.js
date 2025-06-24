/* Modal Window Section */

  // Get elements
  const loginLink = document.getElementById('loginLink');
  const loginModal = document.getElementById('loginModal');
  const closeModal = document.getElementById('closeModal');
  const loginBtn = document.getElementById('loginBtn'); 

// Function to disable body scroll when modal is open
  const disableScroll = () => {
    document.body.classList.add('overflow-hidden');
  };

  // Function to enable body scroll when modal is closed
  const enableScroll = () => {
    document.body.classList.remove('overflow-hidden');
  };

  // Show the modal when login link is clicked
  loginLink.addEventListener('click', () => {
    loginModal.classList.remove('hidden');
    modalOverlay.classList.remove('hidden');
    disableScroll();
  });

  // Hide the modal when close button is clicked
  closeModal.addEventListener('click', () => {
    loginModal.classList.add('hidden');
    modalOverlay.classList.add('hidden');
    enableScroll();
  });

  // Hide the modal when Login button is clicked
  loginBtn.addEventListener('click', () => {
    loginModal.classList.add('hidden');
    modalOverlay.classList.add('hidden');
    enableScroll();
  });