"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChartNoAxesCombined,
  CloudCog,
  Home as HomeIcon,
  Languages,
  LayoutDashboard,
  Network,
  ScanSearch,
  UserRound,
  GraduationCap,
} from "lucide-react";

import type { AuthState } from "@/lib/api";

export type NavbarView =
  | "home"
  | "lab"
  | "dashboard"
  | "stem"
  | "insights"
  | "system";

type NavbarLabels = {
  navHome: string;
  navLab: string;
  navInsights: string;
  navSystem: string;
};

type NavbarProps = {
  activeView: NavbarView;
  labels: NavbarLabels;
  auth: AuthState;
  lang: "en" | "ar";
  platformStatus?: string | null;

  onHome: () => void;
  onLab: () => void;
  onStem: () => void;
  onInsights: () => void;
  onSystem: () => void;
  onToggleLanguage: () => void;
};

export default function Navbar({
  activeView,
  labels,
  auth,
  lang,
  platformStatus,
  onHome,
  onLab,
  onStem,
  onInsights,
  onSystem,
  onToggleLanguage,
}: NavbarProps) {

  const pathname = usePathname();

  const dashboardActive = pathname === "/dashboard";
  const stemActive = pathname === "/stem";

  const viewIsActive = (view: NavbarView) =>
    !dashboardActive &&
    !stemActive &&
    activeView === view;


  return (
    <header className="site-header">

      <button
        className="logo"
        onClick={onHome}
        aria-label="Misconception MRI home"
      >
        <span className="logo-mark">M</span>
        <span className="logo-copy">
          Misconception <b>MRI</b>
        </span>
        <span className="version-badge">
          PLATFORM
        </span>
      </button>


      <nav
        className="main-nav"
        aria-label="Primary navigation"
      >

        <button
          className={viewIsActive("home") ? "active" : ""}
          onClick={onHome}
        >
          <HomeIcon size={15} strokeWidth={1.9}/>
          {labels.navHome}
        </button>


        <button
          className={viewIsActive("lab") ? "active" : ""}
          onClick={onLab}
        >
          <ScanSearch size={15} strokeWidth={1.9}/>
          {labels.navLab}
        </button>


        <Link
          className={dashboardActive ? "active" : ""}
          href="/dashboard"
        >
          <LayoutDashboard size={15} strokeWidth={1.9}/>
          Dashboard
        </Link>


        <button
          className={stemActive ? "active" : ""}
          onClick={onStem}
        >
          <GraduationCap size={15} strokeWidth={1.9}/>
          STEM
        </button>


        <button
          className={viewIsActive("insights") ? "active" : ""}
          onClick={onInsights}
        >
          <ChartNoAxesCombined size={15} strokeWidth={1.9}/>
          {labels.navInsights}
        </button>


        <button
          className={viewIsActive("system") ? "active" : ""}
          onClick={onSystem}
        >
          <Network size={15} strokeWidth={1.9}/>
          {labels.navSystem}
        </button>

      </nav>


      <div className="header-actions">

        <span className="api-status">
          <CloudCog size={14} strokeWidth={1.8}/>
          <i/>
          {platformStatus === "operational"
            ? "OPERATIONAL"
            : "GPT-OSS 120B"}
        </span>


        {auth.authenticated && auth.user ? (

          <Link
            className="account-chip"
            href="/account"
          >
            <UserRound size={14} strokeWidth={1.9}/>
            <span>
              {auth.user.full_name.split(" ")[0]}
            </span>
          </Link>

        ) : (

          <Link
            className="account-chip"
            href="/signin"
          >
            <UserRound size={14} strokeWidth={1.9}/>
            <span>
              Sign in
            </span>
          </Link>

        )}


        <button
          className="lang-switch"
          onClick={onToggleLanguage}
          aria-label="Switch language"
        >
          <Languages size={15} strokeWidth={1.9}/>
          <span>
            {lang === "en" ? "AR" : "EN"}
          </span>
        </button>

      </div>

    </header>
  );
}