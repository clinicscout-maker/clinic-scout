import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function TermsPage() {
    return (
        <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
                <div className="mb-8">
                    <Link
                        href="/"
                        className="inline-flex items-center text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Home
                    </Link>
                </div>

                <div className="bg-white rounded-2xl shadow-sm p-8 sm:p-12">
                    <h1 className="text-3xl font-bold text-slate-900 mb-8">Terms of Service</h1>

                    <div className="space-y-8 text-slate-600">
                        <section>
                            <h2 className="text-xl font-semibold text-slate-900 mb-3">1. Service Description</h2>
                            <p>
                                Clinic Scout is a notification utility designed to alert users about potential availability at medical clinics.
                                <span className="font-bold text-slate-900 block mt-2">
                                    CRITICAL DISCLAIMER: We are NOT a medical provider. We do not guarantee appointments.
                                    Our service is strictly an information tool and does not constitute medical advice or a patient-provider relationship.
                                </span>
                            </p>
                        </section>

                        <section>
                            <h2 className="text-xl font-semibold text-slate-900 mb-3">2. User Conduct</h2>
                            <p>
                                The service is intended for personal use only. You agree not to resell, redistribute, or commercially exploit the alerts provided by Clinic Scout.
                                Any automated scraping or abuse of our API is strictly prohibited.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-xl font-semibold text-slate-900 mb-3">3. Payments and Subscriptions</h2>
                            <p>
                                Access to premium alerts is provided via a monthly subscription managed through Ko-fi.
                                You may cancel your subscription at any time. Please note that we do not offer refunds for partial months or unused service periods.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-xl font-semibold text-slate-900 mb-3">4. Limitation of Liability</h2>
                            <p>
                                We are not responsible for any health outcomes, delays in care, or the actual availability of clinics.
                                Clinic availability changes rapidly, and we cannot guarantee that a spot will be open when you contact a clinic.
                                Use this service at your own risk.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-xl font-semibold text-slate-900 mb-3">5. Termination</h2>
                            <p>
                                We reserve the right to suspend or terminate your access to the service immediately, without prior notice or liability,
                                for any reason whatsoever, including without limitation if you breach these Terms of Service.
                            </p>
                        </section>

                        <div className="pt-8 border-t border-slate-100 text-sm text-slate-500">
                            Last updated: November 2025
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
