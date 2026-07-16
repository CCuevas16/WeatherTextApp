// ======================================================
// DOM ELEMENTS
// ======================================================

//const phoneInput = document.getElementById("phone");
const emailInput = document.getElementById("email");
const stateSelect = document.getElementById("state");
const citySelect = document.getElementById("city");
const signupBtn = document.getElementById("signupBtn");

// ======================================================
// INITIALIZE APPLICATION
// ======================================================

function initApp() {
    loadLocations();
    //setupPhoneFormatter();
    setupEmailInput();
    setupSignupButton();
}

initApp();

// ======================================================
// LOCATION FUNCTIONS
// ======================================================

function loadLocations() {

    fetch("locations.json")
        .then(response => response.json())
        .then(data => {

            populateStates(data.states);

            stateSelect.addEventListener("change", function () {

                clearCities();

                const selectedState = data.states.find(
                    state => state.name === stateSelect.value
                );

                if (!selectedState) return;

                populateCities(selectedState.cities);

            });

        })
        .catch(error => {
            console.error("Error loading locations:", error);
        });

}

function populateStates(states) {

    states.forEach(state => {

        const option = document.createElement("option");

        option.value = state.name;
        option.textContent = state.name;

        stateSelect.appendChild(option);

    });

}

function populateCities(cities) {

    cities.forEach(city => {

        const option = document.createElement("option");

        option.value = city;
        option.textContent = city;

        citySelect.appendChild(option);

    });

}

function clearCities() {

    citySelect.innerHTML =
        '<option value="">Select a City</option>';

}

// ======================================================
// EMAIL FUNCTIONS
// ======================================================

function setupEmailInput() {

    emailInput.addEventListener("input", () => {
        console.log(emailInput.value);
    });

}

function validateEmail() {

    const email = emailInput.value.trim();

    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
        alert("Please enter a valid email address.");
        emailInput.focus();
        return false;
    }

    return true;
}


// function setupPhoneFormatter() {

//     phoneInput.addEventListener("input", function () {

//         let value = phoneInput.value;

//         value = value.replace(/\D/g, "");
//         value = value.substring(0, 10);

//         if (value.length > 6) {
//             value =
//                 `(${value.substring(0,3)}) ${value.substring(3,6)}-${value.substring(6)}`;
//         }
//         else if (value.length > 3) {
//             value =
//                 `(${value.substring(0,3)}) ${value.substring(3)}`;
//         }
//         else if (value.length > 0) {
//             value =
//                 `(${value}`;
//         }

//         phoneInput.value = value;

//     });

// }



// ======================================================
// SIGN UP
// ======================================================

function setupSignupButton() {

    signupBtn.addEventListener("click", validateSignup);

}

function validateSignup() {

    //const phone = phoneInput.value.replace(/\D/g, "");
    const email = emailInput.value.trim();
    const state = stateSelect.value;
    const city = citySelect.value;

    // if (phone.length !== 10) {
    //     console.log("Invalid phone number.");
    //     alert("Please enter a valid 10-digit phone number.");
    //     phoneInput.focus();
    //     return;
    // }
    if (!validateEmail()) return;

    if (state === "") {
        console.log("State not selected.");
        alert("Please select a state.");
        stateSelect.focus();
        return;
    }

    if (city === "") {
        console.log("City not selected.");
        alert("Please select a city.");
        citySelect.focus();
        return;
    }
// ++++++++++ TEST 1 ++++++++++
    // console.log("Signup data is valid!");
    // console.log("Phone:", phone);
    // console.log("State:", state);
    // console.log("City:", city);

    // alert("Registration successful!");

// ++++++++++++++++++++ using this to create json file
    const user = {
        //phone: phone,
        email: email,
        state: state,
        city: city
    };

// ++++++++++ TEST 2 ++++++++++
    console.log("User object:", user);

    alert("Registration successful!");
// ++++++++++++++++++++

saveUserToDatabase(user);

sendUserToPython(user);

}

async function saveUserToDatabase(user) {
    console.log("Sending user to database server:", user);

    try {
        const response = await fetch("http://127.0.0.1:5001/save-user", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(user)
        });

        console.log("Response status:", response.status);

        const result = await response.json();

        console.log("Database server response:", result);

    } catch (error) {
        console.error("Database connection error:", error);
    }
}

// unsubscribeBtn.addEventListener("click", function () {
//     console.log("Unsubscribe button clicked!");
// });
unsubscribeBtn.addEventListener("click", unsubscribeUser);

async function unsubscribeUser() {
    const email = emailInput.value.trim();

    if (!email) {
        alert("Please enter your email address.");
        emailInput.focus();
        return;
    }

    if (!validateEmail()) {
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5001/unsubscribe", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email: email })
        });

        const result = await response.json();

        console.log("Unsubscribe response:", result);

        if (!response.ok) {
            alert(result.message);
            return;
        }

        alert(result.message);
        emailInput.value = "";

    } catch (error) {
        console.error("Unsubscribe error:", error);
        alert("Unable to complete the unsubscribe request.");
    }
}