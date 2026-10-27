import { Container, Nav, Navbar } from "react-bootstrap";
import { BrowserRouter, Link, Route, Routes, useLocation } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import ItemsPage from "./pages/ItemsPage";
import ReportsPage from "./pages/ReportsPage";
import SearchPage from "./pages/SearchPage";
import StockPage from "./pages/StockPage";

const LINKS = [
  { to: "/", label: "Dashboard" },
  { to: "/items", label: "Items" },
  { to: "/search", label: "Search" },
  { to: "/stock", label: "Stock updates" },
  { to: "/reports", label: "Reports" },
];

function NavLinks() {
  const { pathname } = useLocation();
  return (
    <Nav className="me-auto">
      {LINKS.map((l) => (
        <Nav.Link as={Link} to={l.to} key={l.to} active={pathname === l.to}>
          {l.label}
        </Nav.Link>
      ))}
    </Nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar bg="white" expand="md" className="border-bottom mb-4">
        <Container>
          <Navbar.Brand as={Link} to="/">Inventory</Navbar.Brand>
          <Navbar.Toggle aria-controls="main-nav" />
          <Navbar.Collapse id="main-nav">
            <NavLinks />
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <Container className="pb-5">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/items" element={<ItemsPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/stock" element={<StockPage />} />
          <Route path="/reports" element={<ReportsPage />} />
        </Routes>
      </Container>
    </BrowserRouter>
  );
}
