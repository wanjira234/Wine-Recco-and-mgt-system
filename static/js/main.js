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
})

