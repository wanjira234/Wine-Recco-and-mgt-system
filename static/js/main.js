import { Chart } from "@/components/ui/chart"
document.addEventListener("DOMContentLoaded", () => {
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
  document.getElementById('signupForm')?.addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = {
        email: document.getElementById('email').value,
        name: document.getElementById('name').value,
        password: document.getElementById('password').value
    };

    // Store step 1 data in session storage
    sessionStorage.setItem('signupStep1Data', JSON.stringify(formData));

    // Redirect to step 2
    window.location.href = '/auth/signup/step2';
  });

  // Step 2 form submission
  document.getElementById('signupStep2Form')?.addEventListener('submit', function(e) {
    e.preventDefault();

    const step2Data = {
        wine_types: Array.from(document.getElementById('wine_types').selectedOptions).map(opt => opt.value),
        price_range: document.getElementById('price_range').value
    };

    // Store step 2 data in session storage
    sessionStorage.setItem('signupStep2Data', JSON.stringify(step2Data));

    // Redirect to step 3
    window.location.href = '/auth/signup/step3';
  });

  // Step 3 form submission (final step)
  document.getElementById('signupStep3Form')?.addEventListener('submit', function(e) {
    e.preventDefault();

    // Get data from all steps
    const step1Data = JSON.parse(sessionStorage.getItem('signupStep1Data'));
    const step2Data = JSON.parse(sessionStorage.getItem('signupStep2Data'));
    const step3Data = {
        traits: Array.from(document.getElementById('traits').selectedOptions).map(opt => opt.value)
    };

    // Combine all data
    const finalData = {
        ...step1Data,
        wine_preferences: step2Data,
        traits: step3Data.traits
    };

    // Send final data to create account
    fetch('/auth/api/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify(finalData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Clear session storage
            sessionStorage.removeItem('signupStep1Data');
            sessionStorage.removeItem('signupStep2Data');
            
            // Redirect to recommendations
            window.location.href = '/recommendations';
        } else {
            throw new Error(data.message || 'Signup failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error creating account: ' + error.message);
    });
  });

  // Add event listeners for the continue buttons
  document.querySelector('.continue-btn')?.addEventListener('click', function(e) {
    e.preventDefault();
    document.querySelector('form').dispatchEvent(new Event('submit'));
  });
})

