import express, { Request, Response, NextFunction } from "express";
import path from "path";
import { fileURLToPath } from "url";
import cookieParser from "cookie-parser";
import nunjucks from "nunjucks";
import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";
import cors from "cors";
import dotenv from "dotenv";

// Carrega variaveis de ambiente
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

// Configura o segredo do JWT (pelo menos 32 caracteres para seguranca)
const SECRET_KEY = process.env.SECRET_KEY || "uma_chave_secreta_padrao_com_mais_de_32_caracteres_longa";
const SESSION_COOKIE_NAME = "rsdros_session";

// Interfaces de Dominio (Alinhado com as convencoes do AGENTS.md)
interface Organization {
  id: string;
  name: string;
  slug: string;
  brand_name: string | null;
  custom_domain: string | null;
  theme_primary_color: string;
  theme_secondary_color: string;
  theme_logo_url: string | null;
  theme_favicon_url: string | null;
  theme_name?: string;
  plan: string;
  feature_flags: Record<string, any>;
  settings: Record<string, any>;
  contact_email: string | null;
  contact_phone: string | null;
  is_active: boolean;
  trial_ends_at: string | null;
}

interface User {
  id: string;
  organization_id: string;
  email: string;
  name: string;
  password_hash: string;
  role: string;
  is_active: boolean;
  email_verified: boolean;
  email_verified_at: string | null;
  last_login_at: string | null;
  last_login_ip: string | null;
}

// Banco de dados em memoria (Mock alinhado com Phase 2.2)
const organizations: Organization[] = [
  {
    id: "org_bela",
    name: "Clinica Estetica Bela",
    slug: "clinica-bela",
    brand_name: "Bela Estetica",
    custom_domain: null,
    theme_primary_color: "#EC4899",
    theme_secondary_color: "#9D174D",
    theme_logo_url: null,
    theme_favicon_url: null,
    theme_name: "light",
    plan: "trial",
    feature_flags: {},
    settings: {},
    contact_email: "contato@belaclinica.com",
    contact_phone: null,
    is_active: true,
    trial_ends_at: null,
  },
  {
    id: "org_imob",
    name: "Imobiliaria Center",
    slug: "imob-center",
    brand_name: "Imob Center",
    custom_domain: null,
    theme_primary_color: "#10B981",
    theme_secondary_color: "#065F46",
    theme_logo_url: null,
    theme_favicon_url: null,
    theme_name: "luxury",
    plan: "trial",
    feature_flags: {},
    settings: {},
    contact_email: "contato@imobcenter.com",
    contact_phone: null,
    is_active: true,
    trial_ends_at: null,
  }
];

const users: User[] = [
  {
    id: "user_bela_admin",
    organization_id: "org_bela",
    email: "admin@clinica-bela.com",
    name: "Maria Silva",
    password_hash: bcrypt.hashSync(process.env.SEED_ADMIN_PASSWORD || "senha123", 10),
    role: "admin",
    is_active: true,
    email_verified: true,
    email_verified_at: new Date().toISOString(),
    last_login_at: null,
    last_login_ip: null,
  },
  {
    id: "user_imob_admin",
    organization_id: "org_imob",
    email: "admin@imob-center.com",
    name: "Joao Santos",
    password_hash: bcrypt.hashSync(process.env.SEED_ADMIN_PASSWORD || "senha123", 10),
    role: "admin",
    is_active: true,
    email_verified: true,
    email_verified_at: new Date().toISOString(),
    last_login_at: null,
    last_login_ip: null,
  }
];

// Configura o motor de templates Nunjucks (altamente compativel com Jinja2)
nunjucks.configure(path.join(process.cwd(), "app", "web", "templates"), {
  autoescape: true,
  express: app,
  watch: false,
  noCache: true
});

// Middlewares Globais
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// CORS habilitado se configurado em CORS_ORIGINS
const corsOrigins = process.env.CORS_ORIGINS || "";
if (corsOrigins) {
  const allowedOrigins = corsOrigins.split(",").map(origin => origin.trim());
  app.use(cors({
    origin: allowedOrigins,
    credentials: true,
  }));
} else {
  app.use(cors());
}

// Serve arquivos estaticos
app.use("/static", express.static(path.join(process.cwd(), "app", "web", "static")));

// Paths publicas que nao exigem tenant resolvido
const PUBLIC_PATHS = new Set([
  "/",
  "/favicon.ico",
  "/api/v1/health",
  "/api/v1/health/ready"
]);

// Helper para escurecer cores hexadecimais (usado para gerar a cor hover do botao)
function darken(hexColor: string, percent: number = 10): string {
  let value = hexColor.replace("#", "");
  if (value.length !== 6) return "#000000";
  try {
    let r = parseInt(value.substring(0, 2), 16);
    let g = parseInt(value.substring(2, 4), 16);
    let b = parseInt(value.substring(4, 6), 16);
    const factor = (100 - percent) / 100;
    r = Math.max(0, Math.min(255, Math.floor(r * factor)));
    g = Math.max(0, Math.min(255, Math.floor(g * factor)));
    b = Math.max(0, Math.min(255, Math.floor(b * factor)));
    return `#${r.toString(16).padStart(2, "0").toUpperCase()}${g.toString(16).padStart(2, "0").toUpperCase()}${b.toString(16).padStart(2, "0").toUpperCase()}`;
  } catch {
    return "#000000";
  }
}

// Helper para converter cores hexadecimais para RGB (usado em efeitos de brilho)
function hexToRgb(hexColor: string): string {
  let value = hexColor.replace("#", "");
  if (value.length !== 6) return "59, 130, 246";
  try {
    let r = parseInt(value.substring(0, 2), 16);
    let g = parseInt(value.substring(2, 4), 16);
    let b = parseInt(value.substring(4, 6), 16);
    return `${r}, ${g}, ${b}`;
  } catch {
    return "59, 130, 246";
  }
}

// Helper para construir o contexto do tema (White-label por CSS variables)
function buildThemeContext(req: Request) {
  const organization = (req as any).organization as Organization | null;
  const settings = { appName: process.env.APP_NAME || "Revenue SDR OS" };
  const primary = organization?.theme_primary_color || "#3B82F6";
  const secondary = organization?.theme_secondary_color || "#1E40AF";
  const themeName = organization?.theme_name || "light";

  const themeCss = `:root {
  --tenant-primary: ${primary};
  --tenant-secondary: ${secondary};
  --tenant-primary-hover: ${darken(primary, 10)};
  --tenant-primary-rgb: ${hexToRgb(primary)};
  --tenant-secondary-rgb: ${hexToRgb(secondary)};

  /* Map standard color values dynamically for both utility and custom styles */
  --color-primary: ${primary};
  --color-primary-hover: ${darken(primary, 10)};
  --color-secondary: ${secondary};
  --color-background: ${themeName === "luxury" ? "#090A0F" : "#F8FAFC"};
  --color-surface: ${themeName === "luxury" ? "#11131E" : "#FFFFFF"};
  --color-surface-hover: ${themeName === "luxury" ? "#1A1D2D" : "#F1F5F9"};
  --color-text: ${themeName === "luxury" ? "#F8FAFC" : "#0F172A"};
  --color-text-muted: ${themeName === "luxury" ? "#94A3B8" : "#64748B"};
  --color-border: ${themeName === "luxury" ? "#1E293B" : "#E2E8F0"};
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-danger: #EF4444;
  --color-info: #3B82F6;
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --radius: 0.75rem;
}`;

  const name = organization ? (organization.brand_name || organization.name) : settings.appName;
  const favicon = "/static/img/logo-placeholder.svg";
  const brandMeta = `<title>${name}</title>
<link rel="icon" href="${favicon}">
<meta name="application-name" content="${name}">
<meta name="theme-color" content="${primary}">`;

  return {
    request: req,
    organization: organization,
    theme_css: themeCss,
    brand_meta: brandMeta,
    brand_name: name,
    logo_url: "/static/img/logo-placeholder.svg",
    tenant_slug: (req as any).tenantSlug || "",
    theme_name: themeName,
  };
}

// Custom render helper para injetar automaticamente o branding/tema
function render(req: Request, res: Response, templateName: string, context: Record<string, any> = {}, statusCode: number = 200) {
  const themeContext = buildThemeContext(req);
  const fullContext = {
    ...themeContext,
    ...context
  };
  res.status(statusCode);
  return res.render(templateName, fullContext);
}

// 1. Middleware de Resolucao de Tenant (Multi-tenancy)
app.use((req: Request, res: Response, next: NextFunction) => {
  const pathName = req.path;
  
  // Extrai candidatos a slug e host
  const host = (req.headers.host || "").split(":")[0].toLowerCase();
  let slug: string | null = null;

  if (host) {
    const parts = host.split(".");
    if ((parts.length === 2 && parts[1] === "localhost") || (parts.length >= 3 && !/^\d+$/.test(parts[parts.length - 1]))) {
      slug = parts[0];
    }
  }

  const headerSlug = req.headers["x-tenant-slug"];
  if (headerSlug && typeof headerSlug === "string") {
    slug = headerSlug.trim().toLowerCase();
  }

  // Permite override por query param em desenvolvimento/homologacao
  if (!slug && process.env.APP_ENV !== "production") {
    const queryTenant = req.query.tenant;
    if (queryTenant && typeof queryTenant === "string") {
      slug = queryTenant.trim().toLowerCase();
    }
  }

  // Resolucao da Organizacao correspondente
  let organization: Organization | null = null;
  if (host) {
    organization = organizations.find(o => o.custom_domain === host) || null;
  }
  if (!organization && slug) {
    organization = organizations.find(o => o.slug === slug) || null;
  }
  if (!organization && process.env.DEFAULT_TENANT_SLUG) {
    organization = organizations.find(o => o.slug === process.env.DEFAULT_TENANT_SLUG) || null;
    if (organization) {
      slug = process.env.DEFAULT_TENANT_SLUG;
    }
  }

  // Se ainda nao resolveu, tenta extrair da sessao (cookie ou bearer token)
  if (!organization) {
    let token = req.cookies?.[SESSION_COOKIE_NAME];
    if (!token) {
      const authHeader = req.headers.authorization;
      if (authHeader && authHeader.toLowerCase().startsWith("bearer ")) {
        token = authHeader.substring(7).trim();
      }
    }
    if (token) {
      try {
        const payload = jwt.verify(token, SECRET_KEY) as any;
        if (payload && payload.type === "session" && payload.org) {
          organization = organizations.find(o => o.id === payload.org) || null;
          if (organization) {
            slug = organization.slug;
          }
        }
      } catch {
        // Ignora erros de assinatura/token expirado aqui, pois serao tratados no middleware de autenticacao
      }
    }
  }

  (req as any).organization = organization;
  (req as any).tenantSlug = slug;

  // Se o tenant nao for encontrado e o path nao for publico ou estatico
  if (!organization && !PUBLIC_PATHS.has(pathName) && !pathName.startsWith("/static")) {
    if (pathName.startsWith("/api/")) {
      return res.status(404).json({
        error: {
          code: "tenant_not_found",
          message: `Tenant '${slug || host}' not found`,
        }
      });
    } else {
      return render(req, res, "errors/tenant_not_found.html", { tenant_slug: slug || "" }, 404);
    }
  }

  next();
});

// 2. Helper de Extracao e Decodificacao de Token (Cookie & Bearer Auth)
function getAuthenticatedUser(req: Request): User | null {
  let token = req.cookies?.[SESSION_COOKIE_NAME];
  if (!token) {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.toLowerCase().startsWith("bearer ")) {
      token = authHeader.substring(7).trim();
    }
  }

  if (!token) return null;

  try {
    const payload = jwt.verify(token, SECRET_KEY) as any;
    if (!payload || payload.type !== "session") return null;

    // Defesa em profundidade: token de um tenant nao opera em outro tenant
    const requestOrg = (req as any).organization as Organization | null;
    if (requestOrg && payload.org !== requestOrg.id) return null;

    const user = users.find(u => u.id === payload.sub);
    if (!user || !user.is_active || user.organization_id !== payload.org) {
      return null;
    }

    return user;
  } catch {
    return null;
  }
}

// Middleware de Autenticacao (popula req.currentUser de forma lazy/opcional)
app.use((req: Request, res: Response, next: NextFunction) => {
  (req as any).currentUser = getAuthenticatedUser(req);
  next();
});

// ==========================================
// ROTAS HTML (WEB CLIENT)
// ==========================================

// Raiz: redireciona com base no status do usuario
app.get("/", (req: Request, res: Response) => {
  const currentUser = (req as any).currentUser;
  if (currentUser) {
    return res.redirect(303, "/dashboard");
  }
  return res.redirect(303, "/login");
});

// Tela de login
app.get("/login", (req: Request, res: Response) => {
  const currentUser = (req as any).currentUser;
  if (currentUser) {
    return res.redirect(303, "/dashboard");
  }
  return render(req, res, "auth/login.html");
});

// Processamento de login via Formulario do browser
app.post("/login", (req: Request, res: Response) => {
  let organization = (req as any).organization as Organization | null;
  const { email, password } = req.body;

  const user = users.find(u => {
    if (organization) {
      return u.organization_id === organization.id && u.email === email;
    } else {
      return u.email === email;
    }
  });

  if (!user || !bcrypt.compareSync(password, user.password_hash)) {
    return render(req, res, "auth/login.html", { error: "Email ou senha invalidos" }, 401);
  }

  // Se nao tinhamos organizacao mas achamos o usuario, resolvemos a organizacao dele
  if (!organization) {
    organization = organizations.find(o => o.id === user.organization_id) || null;
    if (organization) {
      (req as any).organization = organization;
      (req as any).tenantSlug = organization.slug;
    }
  }

  if (!organization) {
    return render(req, res, "auth/login.html", { error: "Tenant nao encontrado para este usuario" }, 404);
  }

  if (!user.is_active) {
    return render(req, res, "auth/login.html", { error: "Usuario inativo. Contate o administrador." }, 403);
  }

  // Atualiza metadados
  user.last_login_at = new Date().toISOString();
  user.last_login_ip = req.ip || null;

  const sessionDurationDays = parseInt(process.env.SESSION_DURATION_DAYS || "7", 10);
  const token = jwt.sign(
    {
      sub: user.id,
      org: user.organization_id,
      type: "session",
      jti: Math.random().toString(36).substring(2, 15)
    },
    SECRET_KEY,
    { expiresIn: `${sessionDurationDays}d` }
  );

  res.cookie(SESSION_COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.APP_ENV === "production",
    sameSite: "lax",
    maxAge: sessionDurationDays * 24 * 3600 * 1000,
    path: "/"
  });

  return res.redirect(303, "/dashboard");
});

// Dashboard protegido
app.get("/dashboard", (req: Request, res: Response) => {
  const currentUser = (req as any).currentUser as User | null;
  if (!currentUser) {
    return res.redirect(303, "/login");
  }

  const organization = (req as any).organization as Organization;
  return render(req, res, "dashboard/index.html", {
    user_name: currentUser.name,
    user_role: currentUser.role,
    org_name: organization.name,
    primary_color: organization.theme_primary_color
  });
});

// Logout endpoints (GET e POST)
const handleLogout = (req: Request, res: Response) => {
  res.clearCookie(SESSION_COOKIE_NAME, { path: "/" });
  return res.redirect(303, "/login");
};
app.post("/logout", handleLogout);
app.get("/logout", handleLogout);


// ==========================================
// ROTAS JSON API v1 (REST)
// ==========================================

// API de login
app.post("/api/v1/auth/login", (req: Request, res: Response) => {
  let organization = (req as any).organization as Organization | null;
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({
      error: {
        code: "validation_error",
        message: "Email and password are required"
      }
    });
  }

  const user = users.find(u => {
    if (organization) {
      return u.organization_id === organization.id && u.email === email;
    } else {
      return u.email === email;
    }
  });

  if (!user || !bcrypt.compareSync(password, user.password_hash)) {
    return res.status(401).json({
      error: {
        code: "authentication_failed",
        message: "Invalid credentials"
      }
    });
  }

  // Se nao tinhamos organizacao mas achamos o usuario, resolvemos a organizacao dele
  if (!organization) {
    organization = organizations.find(o => o.id === user.organization_id) || null;
    if (organization) {
      (req as any).organization = organization;
      (req as any).tenantSlug = organization.slug;
    }
  }

  if (!organization) {
    return res.status(404).json({
      error: {
        code: "tenant_not_found",
        message: "Organization not found"
      }
    });
  }

  if (!user.is_active) {
    return res.status(403).json({
      error: {
        code: "permission_denied",
        message: "User inactive"
      }
    });
  }

  // Atualiza metadados de login
  user.last_login_at = new Date().toISOString();
  user.last_login_ip = req.ip || null;

  const sessionDurationDays = parseInt(process.env.SESSION_DURATION_DAYS || "7", 10);
  const token = jwt.sign(
    {
      sub: user.id,
      org: user.organization_id,
      type: "session",
      jti: Math.random().toString(36).substring(2, 15)
    },
    SECRET_KEY,
    { expiresIn: `${sessionDurationDays}d` }
  );

  res.cookie(SESSION_COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.APP_ENV === "production",
    sameSite: "lax",
    maxAge: sessionDurationDays * 24 * 3600 * 1000,
    path: "/"
  });

  return res.json({
    access_token: token,
    expires_in: sessionDurationDays * 24 * 3600,
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
      role: user.role,
      is_active: user.is_active,
      organization_id: user.organization_id,
      last_login_at: user.last_login_at
    }
  });
});

// API logout
app.post("/api/v1/auth/logout", (req: Request, res: Response) => {
  const currentUser = (req as any).currentUser;
  if (!currentUser) {
    return res.status(401).json({
      error: {
        code: "authentication_error",
        message: "Not authenticated"
      }
    });
  }
  res.clearCookie(SESSION_COOKIE_NAME, { path: "/" });
  return res.status(204).end();
});

// API /me
app.get("/api/v1/auth/me", (req: Request, res: Response) => {
  const currentUser = (req as any).currentUser as User | null;
  if (!currentUser) {
    return res.status(401).json({
      error: {
        code: "authentication_error",
        message: "Not authenticated"
      }
    });
  }
  return res.json({
    id: currentUser.id,
    email: currentUser.email,
    name: currentUser.name,
    role: currentUser.role,
    is_active: currentUser.is_active,
    organization_id: currentUser.organization_id,
    last_login_at: currentUser.last_login_at
  });
});

// API /organization
app.get("/api/v1/organization", (req: Request, res: Response) => {
  const organization = (req as any).organization as Organization | null;
  if (!organization) {
    return res.status(404).json({
      error: {
        code: "tenant_not_found",
        message: "Organization not found"
      }
    });
  }
  return res.json({
    id: organization.id,
    name: organization.name,
    slug: organization.slug,
    brand_name: organization.brand_name,
    display_name: organization.brand_name || organization.name,
    custom_domain: organization.custom_domain,
    theme_primary_color: organization.theme_primary_color,
    theme_secondary_color: organization.theme_secondary_color,
    logo_url: "/static/img/logo-placeholder.svg",
    plan: organization.plan,
    is_active: organization.is_active
  });
});

// API /health e /health/ready
app.get("/api/v1/health", (req: Request, res: Response) => {
  return res.json({
    status: "ok",
    version: "0.2.0",
    service: "revenue-sdr-os"
  });
});

app.get("/api/v1/health/ready", (req: Request, res: Response) => {
  return res.json({
    status: "ready",
    database: "ok",
    version: "0.2.0"
  });
});

// API de Usuarios (/api/v1/users)
app.get("/api/v1/users", (req: Request, res: Response) => {
  const currentUser = (req as any).currentUser as User | null;
  if (!currentUser) {
    return res.status(401).json({
      error: {
        code: "authentication_error",
        message: "Not authenticated"
      }
    });
  }

  // Filtra apenas usuarios pertencentes ao tenant do usuario autenticado
  const orgUsers = users.filter(u => u.organization_id === currentUser.organization_id);

  const limit = parseInt((req.query.limit as string) || "10", 10);
  const offset = parseInt((req.query.offset as string) || "0", 10);
  const paginated = orgUsers.slice(offset, offset + limit).map(u => ({
    id: u.id,
    email: u.email,
    name: u.name,
    role: u.role,
    is_active: u.is_active,
    organization_id: u.organization_id,
    last_login_at: u.last_login_at
  }));

  return res.json({
    items: paginated,
    total: orgUsers.length,
    limit,
    offset
  });
});

app.get("/api/v1/users/:user_id", (req: Request, res: Response) => {
  const currentUser = (req as any).currentUser as User | null;
  if (!currentUser) {
    return res.status(401).json({
      error: {
        code: "authentication_error",
        message: "Not authenticated"
      }
    });
  }

  const user = users.find(u => u.organization_id === currentUser.organization_id && u.id === req.params.user_id);
  if (!user) {
    return res.status(404).json({
      error: {
        code: "not_found",
        message: "User not found"
      }
    });
  }

  return res.json({
    id: user.id,
    email: user.email,
    name: user.name,
    role: user.role,
    is_active: user.is_active,
    organization_id: user.organization_id,
    last_login_at: user.last_login_at
  });
});

// Error handling fallback middleware
app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  console.error("Internal Server Error:", err);
  if (req.path.startsWith("/api/")) {
    return res.status(500).json({
      error: {
        code: "internal_server_error",
        message: "An internal server error occurred"
      }
    });
  } else {
    return render(req, res, "errors/error.html", { status_code: 500, message: "Erro interno no servidor" }, 500);
  }
});

// Inicializa o servidor Express
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});
