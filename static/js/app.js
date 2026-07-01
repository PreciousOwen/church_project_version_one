// At the very top of your app.js file, add this:
// Get the translation function (falls back to identity function if not available)
const gettext = window.gettext || (msgid => msgid);

// Sidebar toggle (menu) elements
const menuToggle = document.getElementById("menuToggle");
const sidebar = document.getElementById("sidebar");
const sidebarClose = document.getElementById("sidebarClose");
const sidebarBackdrop = document.getElementById("sidebarBackdrop");
const sidebarLinks = sidebar ? sidebar.querySelectorAll("a") : [];

const closeSidebar = () => {
    if (sidebar) {
        sidebar.classList.remove("open");
    }
};

if (menuToggle && sidebar) {
    menuToggle.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });
}

if (sidebarClose) {
    sidebarClose.addEventListener("click", closeSidebar);
}

if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener("click", closeSidebar);
}

sidebarLinks.forEach((link) => {
    link.addEventListener("click", closeSidebar);
});

// Your existing code...
const dependentsFields = document.querySelectorAll(".dependents-field");
dependentsFields.forEach((field) => {
    const input = field.querySelector("input[type=hidden]");
    const list = field.querySelector(".dependents-list");
    const addBtn = field.querySelector(".dependents-add");
    const form = field.closest("form");

    if (!input || !list || !addBtn) {
        return;
    }

    const readRows = () => {
        const rows = Array.from(list.querySelectorAll(".dependents-row"));
        const data = rows
            .map((row) => {
                const name = row.querySelector(".dependents-name").value.trim();
                const dob = row.querySelector(".dependents-dob").value.trim();
                const relation = row.querySelector(".dependents-relation").value.trim();
                if (!name && !dob && !relation) {
                    return null;
                }
                return {
                    full_name: name,
                    dob: dob,
                    relationship: relation,
                };
            })
            .filter(Boolean);
        input.value = JSON.stringify(data);
    };

    const addRow = (value) => {
        const row = document.createElement("tr");
        row.className = "dependents-row";
        // Now using gettext for translations
        row.innerHTML = `
            <td><input class="dependents-name" type="text" placeholder="${gettext('Full name')}" /></td>
            <td><input class="dependents-dob" type="date" /></td>
            <td><input class="dependents-relation" type="text" placeholder="${gettext('Relationship')}" /></td>
            <td><button class="dependents-remove" type="button">${gettext('Remove')}</button></td>
        `;

        const nameInput = row.querySelector(".dependents-name");
        const dobInput = row.querySelector(".dependents-dob");
        const relationInput = row.querySelector(".dependents-relation");
        if (value) {
            nameInput.value = value.full_name || "";
            dobInput.value = value.dob || "";
            relationInput.value = value.relationship || "";
        }

        row.addEventListener("input", readRows);
        row.querySelector(".dependents-remove").addEventListener("click", () => {
            row.remove();
            readRows();
        });

        list.appendChild(row);
    };

    addBtn.addEventListener("click", () => {
        addRow();
        readRows();
    });

    if (form) {
        form.addEventListener("submit", readRows);
    }

    let initial = [];
    if (input.value) {
        try {
            const parsed = JSON.parse(input.value);
            if (Array.isArray(parsed)) {
                initial = parsed;
            }
        } catch (error) {
            initial = [];
        }
    }

    const rowCount = Math.max(4, initial.length);
    for (let i = 0; i < rowCount; i += 1) {
        addRow(initial[i]);
    }
    readRows();
});

const steppers = document.querySelectorAll("[data-stepper]");
steppers.forEach((stepper) => {
    const steps = Array.from(stepper.querySelectorAll(".form-step"));
    let current = 0;

    const showStep = (index) => {
        steps.forEach((step, idx) => {
            if (idx === index) {
                step.removeAttribute("hidden");
            } else {
                step.setAttribute("hidden", "hidden");
            }
        });
    };

    stepper.addEventListener("click", (event) => {
        const target = event.target;
        if (!(target instanceof HTMLElement)) {
            return;
        }
        if (target.hasAttribute("data-next")) {
            current = Math.min(current + 1, steps.length - 1);
            showStep(current);
        }
        if (target.hasAttribute("data-prev")) {
            current = Math.max(current - 1, 0);
            showStep(current);
        }
    });

    showStep(current);
});

const pageLoader = document.getElementById("pageLoader");
const loaderKey = "pageLoaderStart";

const initNumberFormatting = () => {
    if (typeof Cleave === "undefined") {
        return;
    }

    const targets = document.querySelectorAll("[data-cleave]");
    targets.forEach((input) => {
        if (!(input instanceof HTMLInputElement)) {
            return;
        }
        const mode = input.getAttribute("data-cleave");
        if (mode === "number") {
            const decimalAttr = input.getAttribute("data-decimal");
            const allowDecimals = decimalAttr === "true";
            new Cleave(input, {
                numeral: true,
                numeralDecimalScale: allowDecimals ? 2 : 0,
                numeralDecimalMark: ".",
                delimiter: ",",
                numeralThousandsGroupStyle: "thousand",
            });
        }
    });
};

const showPageLoader = () => {
    if (pageLoader) {
        pageLoader.classList.add("is-visible");
    }
};

const hidePageLoader = () => {
    if (pageLoader) {
        pageLoader.classList.remove("is-visible");
    }
};

const initPageLoader = () => {
    if (!pageLoader) {
        return;
    }

    showPageLoader();

    window.addEventListener("load", () => {
        hidePageLoader();
        window.sessionStorage.removeItem(loaderKey);
    });

    window.addEventListener("pageshow", () => {
        hidePageLoader();
        window.sessionStorage.removeItem(loaderKey);
    });
};

document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
        return;
    }

    const link = target.closest("a");
    if (!link) {
        return;
    }

    const href = link.getAttribute("href");
    if (!href || href.startsWith("#") || href.startsWith("javascript:") || href.startsWith("mailto:") || href.startsWith("tel:")) {
        return;
    }

    if (link.getAttribute("target") === "_blank" || link.hasAttribute("download")) {
        return;
    }

    showPageLoader();
    window.sessionStorage.setItem(loaderKey, String(Date.now()));
});

document.addEventListener("submit", (event) => {
    const form = event.target;
    if (form && form.tagName === "FORM") {
        showPageLoader();
        window.sessionStorage.setItem(loaderKey, String(Date.now()));
    }
}, true);

window.addEventListener("beforeunload", () => {
    showPageLoader();
    window.sessionStorage.setItem(loaderKey, String(Date.now()));
});

initPageLoader();
initNumberFormatting();
