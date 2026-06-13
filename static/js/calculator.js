/**
 * Multi-step calculator form controller.
 *
 * Handles step navigation, progress bar updates,
 * live CO₂ preview, and client-side validation.
 */

(function () {
    'use strict';

    // Emission factors (must match backend values)
    const TRANSPORT_FACTORS = {
        car_petrol: 0.192, car_diesel: 0.171, car_cng: 0.130,
        car_electric: 0.050, two_wheeler: 0.052, auto_rickshaw: 0.150,
        bus: 0.089, metro: 0.035, train: 0.041, bicycle: 0.0,
        walking: 0.0, flight_domestic: 0.255, flight_international: 0.195
    };
    const ELECTRICITY_FACTOR = 0.716;
    const LPG_CO2 = 42.5;
    const SOLAR_OFFSET = 4.0 * ELECTRICITY_FACTOR;
    const FOOD_FACTORS = {
        vegan: 0.45, vegetarian: 0.72,
        non_vegetarian: 1.53, heavy_non_veg: 2.38
    };
    const WASTE_FACTOR = 0.58;
    const RECYCLING_REDUCTION = 0.70;
    const WATER_FACTOR = 0.0003;

    let currentStep = 1;
    const totalSteps = 5;

    // DOM elements
    const form = document.getElementById('calculator-form');
    if (!form) return; // Not on calculator page

    const livePreview = document.getElementById('live-co2');
    const progressSteps = document.querySelectorAll('.progress-step');
    const progressLines = document.querySelectorAll('.progress-line');

    /**
     * Show a specific step and hide all others.
     * @param {number} stepNum - The step number to display (1-5)
     */
    function showStep(stepNum) {
        if (stepNum < 1 || stepNum > totalSteps) return;

        document.querySelectorAll('.form-step').forEach(function (step) {
            step.classList.remove('active');
        });

        var targetStep = document.getElementById('step-' + stepNum);
        if (targetStep) {
            targetStep.classList.add('active');
            // Focus on the first input of the new step for accessibility
            var firstInput = targetStep.querySelector('input, select');
            if (firstInput) {
                setTimeout(function () { firstInput.focus(); }, 100);
            }
        }

        currentStep = stepNum;
        updateProgressBar();
        updateLivePreview();
    }

    /**
     * Update progress bar visual state.
     */
    function updateProgressBar() {
        progressSteps.forEach(function (step, index) {
            var stepNum = index + 1;
            step.classList.remove('active', 'completed');
            step.removeAttribute('aria-current');

            if (stepNum === currentStep) {
                step.classList.add('active');
                step.setAttribute('aria-current', 'step');
            } else if (stepNum < currentStep) {
                step.classList.add('completed');
            }
        });

        progressLines.forEach(function (line, index) {
            if (index < currentStep - 1) {
                line.classList.add('filled');
            } else {
                line.classList.remove('filled');
            }
        });

        // Update ARIA progressbar
        var container = document.querySelector('.progress-container');
        if (container) {
            container.setAttribute('aria-valuenow', currentStep);
        }
    }

    /**
     * Calculate live CO₂ estimate from current form values.
     */
    function updateLivePreview() {
        var total = 0;

        // Transport
        var mode = document.getElementById('transport_mode');
        var distance = document.getElementById('transport_distance');
        if (mode && distance && mode.value && distance.value) {
            var factor = TRANSPORT_FACTORS[mode.value] || 0;
            total += factor * Math.max(0, parseFloat(distance.value) || 0);
        }

        // Energy
        var kwh = document.getElementById('electricity_kwh');
        var lpg = document.getElementById('lpg_cylinders');
        var solar = document.getElementById('has_solar');
        if (kwh && kwh.value) {
            total += Math.max(0, parseFloat(kwh.value) || 0) * ELECTRICITY_FACTOR;
        }
        if (lpg && lpg.value) {
            total += (Math.max(0, parseInt(lpg.value) || 0) * LPG_CO2) / 30.0;
        }
        if (solar && solar.checked) {
            total -= SOLAR_OFFSET;
        }
        total = Math.max(total, 0);

        // Food
        var diet = document.getElementById('diet_type');
        var meals = document.getElementById('num_meals');
        if (diet && meals && diet.value && meals.value) {
            var foodFactor = FOOD_FACTORS[diet.value] || 0;
            total += foodFactor * Math.max(0, parseInt(meals.value) || 0);
        }

        // Waste
        var waste = document.getElementById('waste_kg');
        var recycle = document.getElementById('recycling_percentage');
        if (waste && waste.value) {
            var wasteKg = Math.max(0, parseFloat(waste.value) || 0);
            var recyclePct = recycle ? Math.max(0, Math.min(100, parseInt(recycle.value) || 0)) : 0;
            var recycledFraction = recyclePct / 100.0;
            var landfillFraction = 1.0 - recycledFraction;
            total += wasteKg * landfillFraction * WASTE_FACTOR;
            total += wasteKg * recycledFraction * WASTE_FACTOR * (1 - RECYCLING_REDUCTION);
        }

        // Water
        var water = document.getElementById('water_litres');
        if (water && water.value) {
            total += Math.max(0, parseFloat(water.value) || 0) * WATER_FACTOR;
        }

        if (livePreview) {
            livePreview.textContent = total.toFixed(2);
        }
    }

    // Event: Next/Prev step buttons
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('step-next') || e.target.closest('.step-next')) {
            var btn = e.target.classList.contains('step-next') ? e.target : e.target.closest('.step-next');
            var next = parseInt(btn.getAttribute('data-next'));
            if (next) showStep(next);
        }
        if (e.target.classList.contains('step-prev') || e.target.closest('.step-prev')) {
            var btn2 = e.target.classList.contains('step-prev') ? e.target : e.target.closest('.step-prev');
            var prev = parseInt(btn2.getAttribute('data-prev'));
            if (prev) showStep(prev);
        }
    });

    // Event: Progress step clicks
    progressSteps.forEach(function (step) {
        step.addEventListener('click', function () {
            var stepNum = parseInt(this.getAttribute('data-step'));
            if (stepNum) showStep(stepNum);
        });
    });

    // Event: Live preview updates on any input change
    form.addEventListener('input', updateLivePreview);
    form.addEventListener('change', updateLivePreview);

    // Initialize
    showStep(1);
    updateLivePreview();
})();
