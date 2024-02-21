// import { useEffect, useState } from "react";
// import { useAuth } from "../../../context/auth";
// import axios from "axios";

// const UserSaves = () => {
//   const [messages, setMessages] = useState([]);
//   const [loading, setLoading] = useState(false);

//   const [auth] = useAuth();
//   const email = auth?.user?.email;

//   const fetchMessage = async () => {
//     try {
//       setLoading(true);
//       const res = await axios.get(
//         `http://127.0.0.1:5000/api/get_user_saves/${email}`
//       );
//       console.log(res.data.messages);
//       setMessages(res.data.messages);
//       setLoading(false);
//     } catch (error) {
//       // setLoading(false);
//       console.log(error);
//     }
//   };

//   useEffect(() => {
//     fetchMessage();
//   }, []);

//   return (
//     <section>
//       UserSaves
//       <div>
//         {loading ? (
//           <div>Loading...</div>
//         ) : (
//           <div>
//             {messages.map((message, index) => {
//               return (
//                 <div key={index}>
//                   <p>Name: {message.sender_name}</p>
//                   <p>Hospital Name: {message.hospitalName}</p>
//                   <p>Message: {message.message}</p>
//                   <br />
//                 </div>
//               );
//             })}
//           </div>
//         )}
//         {/* {messages.map((message, index) => {
//           return (
//             <li key={index}>
//               <p>Message: {message.message}</p>
//               <p>Name: {message.sender_name}</p>
//             </li>
//           );
//         })} */}
//       </div>
//     </section>
//   );
// };

// export default UserSaves;


// import { useEffect, useState } from "react";
// import { useAuth } from "../../../context/auth";
// import axios from "axios";

// const Admin_SendReport_Saves = () => {
//   const [messages, setMessages] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [downloadLink, setDownloadLink] = useState("");

//   const [auth] = useAuth();
//   const email = auth?.user?.email;
//   // const email = "sathyasivam2004@gmail.com";

//   const fetchMessage = async () => {
//     try {
//       setLoading(true);
//       const res = await axios.get(
//         `http://127.0.0.1:5000/api/admin_get_report_sends/${email}`
//       );
//       console.log(res.data.messages);
//       setMessages(res.data.messages);
//       setLoading(false);
//     } catch (error) {
//       // setLoading(false);
//       console.log(error);
//     }
//   };

//   useEffect(() => {
//     fetchMessage();
//   }, []);

//   const handleDelete = async (_id) => {
//     try {
//       let answer = window.prompt("Are You Sure want to delete this Report?");
//       if (!answer) return;
//       const res = await axios.delete(
//         `http://127.0.0.1:5000/api/admin_send_report_delete/${_id}`
//       );
//       console.log(res.data);
//       fetchMessage();
//       // if(res) console.log("Report Deleted")
//     } catch (error) {
//       console.log(error);
//     }
//   };

//   const fetchPDF = async () => {
//     try {
//       const res = await axios.get(
//         `http://127.0.0.1:5000/api/download?email=${email}`,
//         {
//           responseType: "blob",
//         }
//       );
//       const url = window.URL.createObjectURL(new Blob([res.data]));
//       setDownloadLink(url);
//     } catch (error) {
//       console.log(error);
//     }
//   };

//   return (
//     <section>
//       <div>Report Sended to patients</div>
//       <div>
//         {loading ? (
//           <div>Loading...</div>
//         ) : (
//           <div>
//             {messages.map((message, index) => {
//               return (
//                 <div key={index} className="ml-4 my-5">
//                   <p>Email: {message.receiver_email}</p>
//                   <p>Message: {message.message}</p>x``
//                   <p>Id: {message._id}</p>
//                   <button
//                     className="bg-red-500 rounded px-4 py-2"
//                     onClick={() => handleDelete(message._id)}
//                   >
//                     Delete
//                   </button>
//                   <br />
//                 </div>
//               );
//             })}
//             <button onClick={fetchPDF}>Download PDF</button>
//             {downloadLink && (
//               <div>
//                 <a href={downloadLink} download="downloaded_pdf.pdf">
//                   Download PDF
//                 </a>
//               </div>
//             )}
//           </div>
//         )}

//         {/* {messages.map((message, index) => {
//           return (
//             <li key={index}>
//               <p>Message: {message.message}</p>
//               <p>Name: {message.sender_name}</p>
//             </li>
//           );
//         })} */}
//       </div>
//     </section>
//   );
// };

// export default Admin_SendReport_Saves;


import { useState, useEffect } from "react";
import { useAuth } from "../../../context/auth";
import axios from "axios";
import { FaDownload } from "react-icons/fa6";

function UserSaves() {
  const [auth] = useAuth();
  const [metadata, setMetadata] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userEmail = auth?.user?.email;
        const response = await axios.get(
          `http://127.0.0.1:5000/api/userSaves/metadata?email=${userEmail}`
        );
        setMetadata(response.data);
      } catch (error) {
        console.error("Error fetching metadata:", error);
      }
    };

    fetchData();
  }, []);

  const downloadPdf = async (filename, fileid) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/admin_report_sends?id=${fileid}`
      );
      const data = await response.blob();
      const url = window.URL.createObjectURL(data);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error("Error downloading PDF:", error);
    }
  };

  return (
    <div>
      <h1>Your Reports</h1>
      <div className="relative overflow-x-auto shadow-md sm:rounded-lg m-5">
        <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
          <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-600 dark:text-gray-200">
            <tr>
              <th scope="col" className="px-6 py-3">
                Doctor Name
              </th>
              <th scope="col" className="px-6 py-3">
                Hospital Name
              </th>
              <th scope="col" className="px-6 py-3">
                Mobile
              </th>
              <th scope="col" className="px-6 py-3">
                Email
              </th>
              <th scope="col" className="px-6 py-3">
                Report
              </th>
              <th scope="col" className="px-6 py-3">
                Delete
              </th>
            </tr>
          </thead>
          <tbody>
            {filterMetaData.map((item, index) => (
              <tr
                key={index}
                className="odd:bg-white odd:dark:bg-gray-300 even:bg-gray-50 even:dark:bg-gray-400 border-b dark:border-gray-700"
              >
                <td className="px-6 py-4 font-medium text-gray-600 whitespace-nowrap dark:text-black">
                  {item.PatientId}
                </td>
                <td className="px-6 py-4 font-medium text-gray-600 whitespace-nowrap dark:text-black">
                  {item.ReceiverName}
                </td>
                <td className="px-6 py-4 font-medium text-gray-600 whitespace-nowrap dark:text-black">
                  {item.PatientMobile}
                </td>
                <td className="px-6 py-4 font-medium text-gray-600 whitespace-nowrap dark:text-black">
                  {item.ReceiverEmail}
                </td>
                <td
                  className="px-6 py-4 font-medium text-gray-600 whitespace-nowrap text-[20px] dark:text-black"
                  onClick={() => downloadPdf(item.filename, item._id)}
                >
                  <FaDownload className="w-10" />
                </td>
                
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* <ul>
        {metadata.map((item, index) => (
          <li key={index}>
            <ul className="mb-5">
              <li>
                <strong>Doctor Name:</strong> {item.DoctorName}
              </li>
              <li>
                <strong>Hospital Name:</strong> {item.HospitalName}
              </li>
              <li>
                <strong>Filename:</strong> {item.filename}
              </li>
              {/* {Object.entries(item)
                .filter(([key]) => key !== "filename" && key !== "_id")
                .map(([key, value]) => (
                  <li key={key}>
                    <strong>{key}:</strong> {value}
                  </li>
                ))} 
              <div>
                <button onClick={() => downloadPdf(item.filename, item._id)}>
                  Download PDF
                </button>
              </div>
            </ul>
          </li>
        ))}
      </ul> */}
    </div>
  );
}

export default UserSaves;
