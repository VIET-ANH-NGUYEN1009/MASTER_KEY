const express = require("express");
const app = express();
const cors = require("cors");
const PORT = process.env.PORT || 4000;
app.use(express.json());
app.use(cors());

const sql = require("mssql");
require("dotenv").config();

const config = {
  server: process.env.DB_SERVER,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_DATABASE,
  options: {
    trustServerCertificate: true,
  },
};
const Table_Asset = process.env.Table_Asset;
const UserRight_Control = process.env.UserRight_Control;

const Database_NewAsset = process.env.Database_NewAsset;
const Database_User = process.env.Database_User;

app.get("/api.masterkey/get-info", async (req, res) => {
  const code = req.query.code?.trim();

  try {
    const today = getToday();
    const isAdmin = await getAdmin(code);
    await insertToMasterKey(code);

    if (isAdmin) {
      return res.status(200).json({ code, result: "OK", admin: true });
    }

    const pool = await sql.connect(config);
    const result = await pool
      .request()
      .input("Code", sql.VarChar, code)
      .input("Today", sql.VarChar, today).query(`
        USE ${Database_NewAsset};
        SELECT ID
        FROM ${Table_Asset}
        WHERE Code_Solenoid = @Code
          AND (Verifier != '' OR Verifier IS NOT NULL)
          AND returnStatus IS NULL
          AND CONVERT(date, verifyDate, 102) = @Today
          AND Flag IS NULL
        ORDER BY ID DESC;
      `);

    const records = result.recordset;

    if (records.length > 0) {
      for (const record of records) {
        await Update_GetKey_Flag(record.ID);
      }
      return res.status(200).json({
        code,
        result: "OK",
        admin: false,
      });
    } else {
      return res.status(404).json({
        code,
        result: "NG",
        admin: false,
        message: "No matching records",
      });
    }
  } catch (err) {
    console.error("Query error:", err.message);
    return res.status(500).json({ code, result: "NG", error: err.message });
  } finally {
    await sql.close();
  }
});

async function insertToMasterKey(codeSolenoid) {
  const pool = await sql.connect(config);
  await pool
    .request()
    .input("CodeSolenoid", sql.VarChar, codeSolenoid)
    .input("InsertDate", sql.DateTime, new Date()).query(`
      USE Masterkey;
      DECLARE @FullName NVARCHAR(100); 
      DECLARE @Code NVARCHAR(50);

      SELECT 
        @FullName = a.FullName,
        @Code = a.Code
      FROM UserInformation.dbo.User_Info a
      WHERE TRIM(a.Code_Solenoid) = TRIM(@CodeSolenoid);

      DELETE FROM Code_Solenoid_Checker
      WHERE TRIM(Code_Solenoid) = TRIM(@CodeSolenoid);

      INSERT INTO Code_Solenoid_Checker (Code_Solenoid, DATETIME, FullName, Code)
      VALUES (@CodeSolenoid, @InsertDate, @FullName, @Code);
    `);
}

app.get("/api.masterkey/waiting-unlock", async (req, res) => {
  try {
    const location = req.query.location?.trim();
    const pool = await sql.connect(config);
    const today = getToday();

    const query = `
      USE ${Database_NewAsset};
      SELECT borrower, Borrow_Name, Dept, equipmentName, verifyDate
      FROM ${Table_Asset}
      WHERE (Verifier != '' OR Verifier IS NOT NULL)
        AND returnStatus IS NULL
        AND CONVERT(date, verifyDate, 102) = @Today
        AND Flag IS NULL
        AND Location = @Location
      ORDER BY ID DESC
    `;

    const result = await pool
      .request()
      .input("Location", sql.VarChar, location)
      .input("Today", sql.VarChar, today)
      .query(query);

    const rows = result.recordset;

    const data = rows
      .filter((r) => r.borrower?.trim() !== "")
      .map((r) => ({
        Borrower_Code: r.borrower?.trim() || "",
        Borrower_Name: r.Borrow_Name?.trim() || "",
        Dept: r.Dept?.trim() || "",
        Equip_Name: r.equipmentName?.trim() || "",
        Approval_time: r.verifyDate
          ? new Date(r.verifyDate).toISOString().split("T")[0]
          : "",
      }));

    const resultStatus = data.length > 0 ? "OK" : "NG";

    res.send({
      result: resultStatus,
      location,
      data,
    });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).send({
      result: "NG",
      message: "Error NG",
      data: [],
    });
  }
});

app.get("/api.masterkey/masterkey-history", async (req, res) => {
  try {
    const location = req.query.location?.trim();
    const pool = await sql.connect(config);
    const today = getToday();

    const query = `
      USE ${Database_NewAsset}
      SELECT borrower, Borrow_Name, Dept, equipmentName, verifyDate
      FROM ${Table_Asset}
      WHERE (Verifier != '' OR Verifier IS NOT NULL)
        AND returnStatus IS NULL
        AND CONVERT(date, verifyDate, 102) = @Today
        AND Flag IS NULL
        AND Location = @Location
      ORDER BY ID DESC
    `;

    const result = await pool
      .request()
      .input("Location", sql.VarChar, location)
      .input("Today", sql.VarChar, today)
      .query(query);

    const rows = result.recordset;

    const data = rows
      .filter((r) => r.borrower?.trim() !== "")
      .map((r) => ({
        Borrower_Code: r.borrower?.trim() || "",
        Borrower_Name: r.Borrow_Name?.trim() || "",
        Dept: r.Dept?.trim() || "",
        Equip_Name: r.equipmentName?.trim() || "",
        Approval_time: r.verifyDate
          ? new Date(r.verifyDate).toISOString().split("T")[0]
          : "",
      }));

    const resultStatus = data.length > 0 ? "OK" : "NG";

    res.send({
      result: resultStatus,
      location,
      data,
    });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).send({
      result: "NG",
      message: "Error NG",
      data: [],
    });
  }
});

function getToday() {
  const today = new Date();
  const year = today.getFullYear();
  const month = fillNumber(today.getMonth() + 1); // Months are 0-based
  const day = fillNumber(today.getDate());
  return `${year}-${month}-${day}`;
}
function getTime() {
  const now = new Date();
  const hour = now.getHours();
  const minutes = fillNumber(now.getMinutes());
  const seconds = fillNumber(now.getSeconds());
  return `${hour}:${minutes}:${seconds}`;
}

function fillNumber(number) {
  return number < 10 ? `0${number}` : `${number}`;
}

async function Update_GetKey_Flag(ID) {
  try {
    const masterTime = getTime();
    const query = `
      USE ${Database_NewAsset}
      UPDATE ${Table_Asset}
            SET Flag = 1,
                MasterKey_Time = @masterTime
            WHERE ID = @ID
    `;
    const pool = await sql.connect(config);
    await pool
      .request()
      .input("masterTime", sql.VarChar, masterTime)

      .input("ID", sql.Int, ID)
      .query(query);
  } catch (error) {
    console.error("Error updating LendingHistory:", err.message);
  } finally {
    await sql.close();
  }
}

app.put("/api.masterkey/Update_GetKey_Flag", async (req, res) => {
  const ID = parseInt(req.query.id);

  if (isNaN(ID)) {
    return res.status(400).send({ status: "NG" });
  }

  try {
    await Update_GetKey_Flag(ID);
    res
      .status(200)
      .send({ status: "OK", message: `Flag updated for ID ${ID}` });
  } catch (error) {
    res.status(500).send({ status: "NG", error: error.message });
  }
});

async function getAdmin(code) {
  let result = false;
  const trimmedCode = code.trim();

  try {
    const pool = await sql.connect(config);
    const query = `
    USE ${Database_User};
      SELECT ASSET_Approve 
      FROM ${UserRight_Control} 
      WHERE Code_Solenoid = @code
    `;

    const data = await pool
      .request()
      .input("code", sql.VarChar, trimmedCode)
      .query(query);

    const rows = data.recordset;
    console.log(
      rows,
      " - ",
      rows[0],
      " - ",
      rows[0].ASSET_Approve,
      " - ",
      typeof rows[0].ASSET_Approve
    );

    if (rows.length > 0) {
      const value = rows[0].ASSET_Approve;
      result = value ? true : false;
    }
  } catch (error) {
    console.error("Error getting admin status:", error.message);
    result = false;
  } finally {
    await sql.close();
  }

  return result;
}

app.get("/api.masterkey/get_admin", async (req, res) => {
  const code = req.query.code?.trim();

  try {
    const status = await getAdmin(code);
    res.status(200).send({ code, adminStatus: status });
  } catch (error) {
    console.error("Error in /get_admin:", error.message);
    res.status(500).send({ error: "Something went wrong" });
  }
});

// GOI CODE_SOLENOID
app.get("/api.masterkey/get_code", async (req, res) => {
  try {
    const pool = await sql.connect(config);
    const result = await pool.request().query(`
      USE Masterkey;
      SELECT TOP 5 a.Code_solenoid, b.Code, b.FullName, a.DATETIME
      FROM Code_Solenoid_Checker a
      LEFT JOIN UserInformation.dbo.User_Info b
      on trim(a.Code_solenoid) = trim(b.Code_Solenoid)
      ORDER BY a.ID DESC;
    `);

    const rows = result.recordset;
    if (rows.length > 0) {
      res.status(200).json({
        result: "OK",
        code_solenoids: rows.map((row) => ({
          Code_solenoid: row.Code_solenoid,
          Code: row.Code,
          FullName: row.FullName,
          DATETIME: row.DATETIME.toLocaleString(),
        })),
      });
    } else {
      res.status(404).json({ result: "NG", message: "data fail." });
    }
  } catch (error) {
    console.error("error query:", error.message);
    res.status(500).json({ result: "NG", error: error.message });
  } finally {
    await sql.close();
  }
});

app.get("/api.masterkey/get_name", async (req, res) => {
  const code = req.query.code?.trim();

  const get_name = async (code) => {
    try {
      const pool = await sql.connect(config);
      const result = await pool.request().input("code", sql.VarChar, code)
        .query(`
        USE UserInformation;
        SELECT TOP 1 Code, FullName, Code_solenoid, Grade, Dept
        FROM User_Info
        WHERE Code = @code
        ORDER BY ID DESC;
      `);

      const rows = result.recordset;

      return {
        success: true,
        data: rows.map((row) => ({
          Code_solenoid: row.Code_solenoid,
          Code: row.Code,
          FullName: row.FullName,
          Grade: row.Grade,
          Dept: row.Dept,
        })),
      };
    } catch (error) {
      console.error("Error query:", error.message);
      return { success: false, error: error.message };
    } finally {
      await sql.close();
    }
  };

  const result = await get_name(code);

  if (result.success && result.data.length > 0) {
    res.status(200).json({ result: "OK", info: result.data[0] });
  } else if (result.success) {
    res.status(404).json({ result: "NG", message: "No find data." });
  } else {
    res.status(500).json({ result: "NG", error: result.error });
  }
});

app.post("/api.masterkey/update_code", async (req, res) => {
  const { codeSolenoid, code } = req.body;

  try {
    const pool = await sql.connect(config);
    console.log(pool);

    const no_codesolenoid = async (codeSolenoid) => {
      console.log(codeSolenoid);
      const pool = await sql.connect(config);
      const result = await pool
        .request()
        .input("codeSolenoid", sql.VarChar, codeSolenoid).query(`
      USE ${process.env.DATABASE_USER};
      SELECT * FROM ${process.env.TABLE_USER}
      WHERE Code_Solenoid = @codeSolenoid;
    `);
      return result.recordset.length > 0;
    };

    const exists = await no_codesolenoid(codeSolenoid);
    if (exists) {
      return res.status(409).json({
        result: "FAIL",
      });
    }

    const updateResult = await pool
      .request()
      .input("codeSolenoid", sql.VarChar, codeSolenoid)
      .input("code", sql.VarChar, code).query(`
        USE ${process.env.DATABASE_USER};
        UPDATE ${process.env.TABLE_USER}
        SET Code_Solenoid = @codeSolenoid
        WHERE Code = @code;
      `);

    if (updateResult.rowsAffected[0] === 0) {
      return res.status(404).json({
        result: "FAIL",
      });
    }

    res.status(200).json({
      result: "OK",
      message: "Update success.",
      updatedCode: code,
      newCodeSolenoid: codeSolenoid,
      rowsAffected: updateResult.rowsAffected[0],
    });
  } catch (err) {
    console.error("SQL Error:", err);
    res.status(500).json({ result: "FAIL", message: "SQL Error." });
  }
});

// Khởi động server
app.listen(PORT, () => {
  console.log(`Server conected ${PORT}`);
});
