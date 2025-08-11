const btnReceive = document.querySelector(".btn_code");
const inputCode = document.querySelector(".code input");
const infoList = document.querySelector("#info_list");
const tableBody = document.querySelector("#solenoidTable tbody");
const code_input = document.querySelectorAll("#code_input");
const messages = document.querySelectorAll("#message");
// const getcode = document.querySelector(".btn_code_solenoid");
// const BE_BASEPATH = "http://10.0.108.10:99";
const BE_BASEPATH = "http://localhost:4000";
document.addEventListener("DOMContentLoaded", async () => {
  const API_URL = `${BE_BASEPATH}/api.masterkey/get_code`;

  try {
    const response = await fetch(API_URL);
    const data = await response.json();
    console.log(data);

    if (response.ok && data.result === "OK") {
      tableBody.innerHTML = "";
      data.code_solenoids.forEach((item, index) => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td >${index + 1}</td>
          <td id ="txtSolenoid_${index + 1}">${item.Code_solenoid}</td>
          <td>
            <input id=${
              index + 1
            } style="padding: 8px; font-size: 16px" value=${item.Code || ""} >
          </td>
          <td>${item.FullName}</td>
          <td>${item.DATETIME}</td>
          <td>
            <button 
              onclick="updateData(${index + 1}, ${item.Code_solenoid})"
              class="btn_update_row" 
              data-code="${item.Code}" 
              data-code-solenoid="${item.Code_solenoid}"
            >
              Update
            </button>
          </td>
        `;

        tableBody.appendChild(row);
      });
    } else {
      tableBody.innerHTML = `
        <tr>
          <td colspan="5">Không có dữ liệu</td>
        </tr>
      `;
    }
  } catch (error) {
    console.error("Error loading data:", error);
    tableBody.innerHTML = `
      <tr>
        <td colspan="5">Lỗi kết nối server</td>
      </tr>
    `;
  }
});

document.addEventListener("DOMContentLoaded", () => {
  btnReceive.addEventListener("click", async (event) => {
    event.preventDefault();

    const code = inputCode.value.trim();
    if (!code) {
      alert("Vui lòng nhập code.");
      return;
    }
    callGetData(code, infoList);
  });
});

document.addEventListener("DOMContentLoaded", () => {
  btnReceive.addEventListener("click", async (event) => {
    event.preventDefault();

    const code = inputCode.value.trim();
    if (!code) {
      alert("Vui lòng nhập code.");
      return;
    }

    try {
      const response = await fetch(
        `${BE_BASEPATH}/api.masterkey/get_name?code=${code}`
      );
      const data = await response.json();

      infoList.innerHTML = "";

      if (response.ok && data.result === "OK") {
        const info = data.info;

        for (const [key, value] of Object.entries(info)) {
          const li = document.createElement("li");
          li.textContent = `${key}: ${value}`;
          infoList.appendChild(li);
        }
      } else {
        const li = document.createElement("li");
        li.textContent = data.message || "Không tìm thấy thông tin.";
        infoList.appendChild(li);
      }
    } catch (error) {
      console.error("Lỗi khi gọi get_name:", error);
      infoList.innerHTML = "<li>Lỗi kết nối đến server.</li>";
    }
  });
});

const callGetData = async (code, infoList) => {
  try {
    const response = await fetch(
      `${BE_BASEPATH}/api.masterkey/get_name?code=${code}`
    );
    const data = await response.json();

    infoList.innerHTML = "";

    if (response.ok && data.result === "OK") {
      const info = data.info;

      for (const [key, value] of Object.entries(info)) {
        const li = document.createElement("li");
        li.id = `${key}`;
        li.textContent = `${key}: ${value}`;
        infoList.appendChild(li);
      }
    } else {
      const li = document.createElement("li");
      li.textContent = data.message || "Không tìm thấy thông tin.";
      infoList.appendChild(li);
    }
  } catch (error) {
    console.error("Lỗi khi gọi get_name:", error);
    infoList.innerHTML = "<li>Lỗi kết nối đến server.</li>";
  }
};

// document.addEventListener("DOMContentLoaded", () => {
//   tableBody.addEventListener("click", async (event) => {
//     if (event.target.classList.contains("btn_update_row")) {
//       const button = event.target;
//       const codeSolenoid = button.dataset.codeSolenoid;
//       const codeID = document.querySelector(".code input");
//       code = codeID.value.trim();
//       const row = button.closest("tr");
//       const index = row.rowIndex;

//       await updateData(index, code, codeSolenoid, button);
//     }
//   });
// });

const updateData = async (index, codeSolenoid) => {
  try {
    const code = document.getElementById(index).value;

    const response = await fetch(`${BE_BASEPATH}/api.masterkey/update_code`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ codeSolenoid: codeSolenoid.toString(), code }),
    });

    const data = await response.json();

    if (response.ok && data.result === "OK") {
      alert(`Update Code solenoid ${codeSolenoid} success for code ${code}!`);
      location.reload();
    } else {
      alert(` Lỗi: ${data.message || "Update fail"}`);
    }
  } catch (error) {
    console.error(error);
    alert(" Error server.");
  }
};

// code_input.forEach((input, index) => {
//   input.addEventListener("blur", () => {
//     const isEmpty = input.value.trim() === "";
//     messages[index].style.display = isEmpty ? "block" : "none";
//   });
// });
