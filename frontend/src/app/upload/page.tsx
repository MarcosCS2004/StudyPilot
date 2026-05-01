import type { Metadata } from "next";
import ExamAutopsyReport from "@/components/ExamAutopsyReport";

export const metadata: Metadata = {
  title: "Materiales y Apuntes",
  description: "Sube tus apuntes, PDFs, imágenes y documentos para que el tutor IA los aprenda.",
};

export default function UploadPage() {
  // Renders only the upload center section (notes tab active by default)
  return <ExamAutopsyReport />;
}
