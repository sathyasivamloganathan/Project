import { Outlet, useNavigate } from "react-router-dom"
const UserDashboard = ({currentUser}) => {
  const navigate = useNavigate();
  return (
      currentUser === "user" ? 
      (
        <>
        {/* <Routes>
          <Route path="/upload" element={<Upload />}/>
        </Routes> */}
        {/* <div>jhhb</div> */}
        <Outlet />
        </>
        
      ) : (navigate('/unauthorized'))
  )
}

export default UserDashboard    