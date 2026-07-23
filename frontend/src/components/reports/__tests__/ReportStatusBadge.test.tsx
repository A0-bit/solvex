import React from "react";
import { render, screen } from "@testing-library/react";
import ReportStatusBadge from "../ReportStatusBadge";

describe("ReportStatusBadge", () => {
  const cases: Array<[string, string]> = [
    ["pending", "Pending"],
    ["assigned", "Assigned"],
    ["in_progress", "In Progress"],
    ["resolved", "Resolved"],
    ["rejected", "Rejected"],
  ];

  test.each(cases)("renders label for status %s", (status, label) => {
    render(<ReportStatusBadge status={status as never} />);
    expect(screen.getByText(label)).toBeInTheDocument();
  });

  it("applies green colour for resolved", () => {
    render(<ReportStatusBadge status="resolved" />);
    expect(screen.getByText("Resolved").className).toContain("green");
  });

  it("applies red colour for rejected", () => {
    render(<ReportStatusBadge status="rejected" />);
    expect(screen.getByText("Rejected").className).toContain("red");
  });
});
