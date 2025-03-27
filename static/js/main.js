document.addEventListener("DOMContentLoaded", () => {
  // Restore form state if it exists
  const savedFormState = sessionStorage.getItem('formState');
  if (savedFormState) {
    try {
      const formState = JSON.parse(savedFormState);
      Object.entries(formState).forEach(([name, value]) => {
        const input = document.querySelector(`[name="${name}"]`);
        if (input) {
          if (input.type === 'checkbox' || input.type === 'radio') {
            input.checked = value;
          } else {
            input.value = value;
          }
        }
      });
      // Clear the saved state after restoring
      sessionStorage.removeItem('formState');
    } catch (error) {
      console.error('Error restoring form state:', error);
    }
  }

  // Form validation
  const forms = document.querySelectorAll(".needs-validation")

  Array.from(forms).forEach((form) => {
    form.addEventListener(
      "submit",
      (event) => {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }

        form.classList.add("was-validated")
      },
      false,
    )
  })

  // Password visibility toggle
  const passwordInputs = document.querySelectorAll('input[type="password"]')
  passwordInputs.forEach(input => {
    const wrapper = input.parentElement
    const toggleButton = document.createElement('button')
    toggleButton.type = 'button'
    toggleButton.className = 'btn btn-outline-secondary'
    toggleButton.innerHTML = '<i class="fas fa-eye"></i>'
    wrapper.appendChild(toggleButton)

    toggleButton.addEventListener('click', () => {
      const type = input.getAttribute('type') === 'password' ? 'text' : 'password'
      input.setAttribute('type', type)
      toggleButton.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>'
    })
  })

  // Wine trait selection
  const traitOptions = document.querySelectorAll(".trait-option")

  traitOptions.forEach((option) => {
    option.addEventListener("click", function () {
      const input = this.querySelector('input[type="checkbox"], input[type="radio"]')

      if (input.type === "checkbox") {
        input.checked = !input.checked
        this.classList.toggle("selected", input.checked)
      } else if (input.type === "radio") {
        const name = input.name
        document.querySelectorAll(`input[name="${name}"]`).forEach((radio) => {
          radio.closest(".trait-option").classList.remove("selected")
        })

        input.checked = true
        this.classList.add("selected")
      }
    })
  })

  // Multi-step form navigation
  const multiStepForms = document.querySelectorAll(".multi-step-form")

  multiStepForms.forEach((form) => {
    const steps = form.querySelectorAll(".form-step")
    const nextBtns = form.querySelectorAll(".btn-next")
    const prevBtns = form.querySelectorAll(".btn-prev")
    const stepIndicators = document.querySelectorAll(".step")

    let currentStep = 0

    // Show the first step
    showStep(currentStep)

    nextBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        // Validate current step before proceeding
        const currentStepElement = steps[currentStep]
        const inputs = currentStepElement.querySelectorAll("input, select, textarea")
        let isValid = true

        inputs.forEach((input) => {
          if (!input.checkValidity()) {
            isValid = false
            input.classList.add("is-invalid")
          } else {
            input.classList.remove("is-invalid")
          }
        })

        if (isValid) {
          currentStep++
          showStep(currentStep)
        }
      })
    })

    prevBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        currentStep--
        showStep(currentStep)
      })
    })

    function showStep(stepIndex) {
      steps.forEach((step, index) => {
        step.style.display = index === stepIndex ? "block" : "none"
      })

      // Update step indicators
      stepIndicators.forEach((indicator, index) => {
        if (index < stepIndex) {
          indicator.classList.add("completed")
          indicator.classList.remove("active")
        } else if (index === stepIndex) {
          indicator.classList.add("active")
          indicator.classList.remove("completed")
        } else {
          indicator.classList.remove("active", "completed")
        }
      })

      // Show/hide prev/next buttons
      prevBtns.forEach((btn) => {
        btn.style.display = stepIndex === 0 ? "none" : "inline-block"
      })

      const isLastStep = stepIndex === steps.length - 1
      nextBtns.forEach((btn) => {
        if (isLastStep) {
          btn.textContent = "Submit"
          btn.classList.add("btn-success")
          btn.type = "submit"
        } else {
          btn.textContent = "Next"
          btn.classList.remove("btn-success")
          btn.type = "button"
        }
      })
    }
  })

  // Catalog page filters
  const filterForm = document.getElementById("filter-form")
  if (filterForm) {
    filterForm.addEventListener("change", function () {
      this.submit()
    })
  }

  // Price range slider
  const priceRange = document.getElementById("price-range")
  const priceValue = document.getElementById("price-value")

  if (priceRange && priceValue) {
    priceRange.addEventListener("input", function () {
      priceValue.textContent = `$${this.value}`
    })
  }

  // Admin dashboard charts
  if (typeof Chart !== "undefined") {
    // User growth chart
    const userGrowthCtx = document.getElementById("userGrowthChart")
    if (userGrowthCtx) {
      new Chart(userGrowthCtx, {
        type: "line",
        data: {
          labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
          datasets: [
            {
              label: "New Users",
              data: [65, 78, 90, 115, 135, 158],
              borderColor: "#722F37",
              tension: 0.1,
              fill: false,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      })
    }

    // Wine categories chart
    const wineCategoriesCtx = document.getElementById("wineCategoriesChart")
    if (wineCategoriesCtx) {
      new Chart(wineCategoriesCtx, {
        type: "doughnut",
        data: {
          labels: ["Red", "White", "Rosé", "Sparkling", "Dessert"],
          datasets: [
            {
              data: [45, 30, 15, 7, 3],
              backgroundColor: ["#722F37", "#D4AF37", "#E09999", "#B5D8CC", "#9B7653"],
            },
          ],
        },
        options: {
          responsive: true,
        },
      })
    }
  }

  // Signup form submission
  document.getElementById('signupForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    console.log('Signup form submitted');

    // Clear any existing alerts
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
      alertContainer.innerHTML = '';
    }

    try {
      const formData = {
        email: document.getElementById('email').value,
        name: document.getElementById('name').value,
        password: document.getElementById('password').value,
        step: 1
      };

      console.log('Form data collected:', {
        ...formData,
        password: '[REDACTED]'
      });

      // Get CSRF token
      const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
      if (!csrfToken) {
        throw new Error('CSRF token not found');
      }

      // Send data to the server
      const response = await fetch('/auth/api/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      console.log('Server response received:', response.status);
      
      const data = await response.json();
      console.log('Server response data:', {
        ...data,
        access_token: data.access_token ? '[REDACTED]' : undefined
      });

      if (response.status === 409) {
        // Email already registered
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-warning alert-dismissible fade show';
        alertDiv.innerHTML = `
          This email is already registered. Please <a href="/auth/login">login</a> or use a different email.
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        alertContainer.appendChild(alertDiv);
        return;
      }

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      if (data.success) {
        // Store the access token
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token);
          console.log('Access token stored in localStorage');
        }
        // Store step 1 data in session storage
        sessionStorage.setItem('signupStep1Data', JSON.stringify(formData));
        console.log('Step 1 data stored in session storage');
        // Redirect to step 2
        console.log('Redirecting to step 2');
        window.location.href = '/auth/signup/step2';
      } else {
        throw new Error(data.message || 'Signup failed');
      }
    } catch (error) {
      console.error('Error:', error);
      // Show error message to user
      const alertDiv = document.createElement('div');
      alertDiv.className = 'alert alert-danger alert-dismissible fade show';
      alertDiv.innerHTML = `
        ${error.message || 'An error occurred during signup. Please try again.'}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `;
      alertContainer.appendChild(alertDiv);
    }
  });

  // Step 2 form submission
  document.getElementById('signupStep2Form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    console.log('Step 2 form submitted');

    const step2Data = {
        wine_types: Array.from(document.getElementById('wine_types').selectedOptions).map(opt => opt.value),
        price_range: document.getElementById('price_range').value,
        step: 2  // Add step parameter
    };

    console.log('Step 2 data collected:', step2Data);

    // Get CSRF token
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
    if (!csrfToken) {
        console.error('CSRF token not found');
        return;
    }

    // Get access token
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        console.error('Access token not found');
        return;
    }

    // Send data to the server
    fetch('/auth/api/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Authorization': `Bearer ${accessToken}`
        },
        credentials: 'include',  // Include cookies
        body: JSON.stringify(step2Data)
    })
    .then(response => {
        console.log('Server response received:', response.status);
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Server response data:', data);
        if (data.success) {
            // Store step 2 data in session storage
            sessionStorage.setItem('signupStep2Data', JSON.stringify(step2Data));
            console.log('Step 2 data stored in session storage');
            // Redirect to step 3
            console.log('Redirecting to step 3');
            window.location.href = '/auth/signup/step3';
        } else {
            throw new Error(data.message || 'Step 2 failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Show error message to user
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            ${error.message || 'An error occurred. Please try again.'}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.innerHTML = ''; // Clear previous alerts
            alertContainer.appendChild(alertDiv);
        } else {
            console.error('Alert container not found');
        }
    });
  });

  // Step 3 form submission (final step)
  document.getElementById('signupStep3Form')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    console.log('Step 3 form submitted');

    try {
      // Get data from all steps
      const step1Data = JSON.parse(sessionStorage.getItem('signupStep1Data'));
      const step2Data = JSON.parse(sessionStorage.getItem('signupStep2Data'));
      const step3Data = {
        preferences: Array.from(document.querySelectorAll('input[name="preferences"]:checked')).map(input => input.value),
        step: 3
      };

      // Combine all data
      const finalData = {
        ...step1Data,
        ...step2Data,
        ...step3Data
      };

      console.log('Final form data:', {
        ...finalData,
        password: '[REDACTED]'
      });

      // Get CSRF token
      const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
      if (!csrfToken) {
        throw new Error('CSRF token not found');
      }

      // Get access token
      const accessToken = localStorage.getItem('access_token');
      if (!accessToken) {
        throw new Error('Access token not found');
      }

      // Send the complete data to the server
      const response = await fetch('/auth/api/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
          'Authorization': `Bearer ${accessToken}`
        },
        credentials: 'include',
        body: JSON.stringify(finalData)
      });

      console.log('Server response received:', response.status);
      
      const data = await response.json();
      console.log('Server response data:', data);

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      if (data.success) {
        // Clear session storage
        sessionStorage.removeItem('signupStep1Data');
        sessionStorage.removeItem('signupStep2Data');
        console.log('Signup completed successfully');
        // Redirect to success page or dashboard
        window.location.href = '/';
      } else {
        throw new Error(data.message || 'Signup failed');
      }
    } catch (error) {
      console.error('Error:', error);
      // Show error message to user
      const alertDiv = document.createElement('div');
      alertDiv.className = 'alert alert-danger alert-dismissible fade show';
      alertDiv.innerHTML = `
        ${error.message || 'An error occurred during signup. Please try again.'}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `;
      const alertContainer = document.getElementById('alert-container');
      if (alertContainer) {
        alertContainer.innerHTML = ''; // Clear previous alerts
        alertContainer.appendChild(alertDiv);
      } else {
        console.error('Alert container not found');
      }
    }
  });

  // Add event listeners for the continue buttons
  document.querySelector('.continue-btn')?.addEventListener('click', function(e) {
    e.preventDefault();
    document.querySelector('form').dispatchEvent(new Event('submit'));
  });
})

