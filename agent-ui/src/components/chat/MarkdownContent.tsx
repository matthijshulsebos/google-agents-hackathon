import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownContentProps {
  content: string;
}

const MarkdownContent: React.FC<MarkdownContentProps> = ({ content }) => {
  return (
    <div className="prose prose-sm max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
        // Headings
        h1: ({ node, ...props }) => (
          <h1 className="text-lg font-bold text-gray-900 mt-4 mb-2" {...props} />
        ),
        h2: ({ node, ...props }) => (
          <h2 className="text-base font-bold text-gray-900 mt-3 mb-2" {...props} />
        ),
        h3: ({ node, ...props }) => (
          <h3 className="text-sm font-semibold text-gray-900 mt-2 mb-1" {...props} />
        ),
        h4: ({ node, ...props }) => (
          <h4 className="text-sm font-semibold text-gray-800 mt-2 mb-1" {...props} />
        ),

        // Paragraphs
        p: ({ node, ...props }) => (
          <p className="text-sm text-gray-800 mb-2 leading-relaxed" {...props} />
        ),

        // Lists
        ul: ({ node, ...props }) => (
          <ul className="text-sm text-gray-800 mb-2 ml-4 list-disc space-y-1" {...props} />
        ),
        ol: ({ node, ...props }) => (
          <ol className="text-sm text-gray-800 mb-2 ml-4 list-decimal space-y-1" {...props} />
        ),
        li: ({ node, ...props }) => (
          <li className="text-sm text-gray-800" {...props} />
        ),

        // Strong/Bold
        strong: ({ node, ...props }) => (
          <strong className="font-bold text-gray-900" {...props} />
        ),

        // Emphasis/Italic
        em: ({ node, ...props }) => (
          <em className="italic text-gray-700" {...props} />
        ),

        // Code
        code: ({ node, inline, ...props }: any) => (
          inline ? (
            <code className="bg-gray-200 text-gray-900 px-1.5 py-0.5 rounded text-xs font-mono" {...props} />
          ) : (
            <code className="block bg-gray-200 text-gray-900 p-2 rounded text-xs font-mono overflow-x-auto my-2" {...props} />
          )
        ),

        // Blockquote
        blockquote: ({ node, ...props }) => (
          <blockquote className="border-l-4 border-gray-300 pl-3 italic text-gray-700 my-2" {...props} />
        ),

        // Links
        a: ({ node, ...props }) => (
          <a className="text-primary hover:text-primary-dark underline" target="_blank" rel="noopener noreferrer" {...props} />
        ),

        // Horizontal Rule
        hr: ({ node, ...props }) => (
          <hr className="my-3 border-gray-300" {...props} />
        ),

        // Tables
        table: ({ node, ...props }) => (
          <div className="overflow-x-auto my-2">
            <table className="min-w-full text-sm border-collapse" {...props} />
          </div>
        ),
        thead: ({ node, ...props }) => (
          <thead className="bg-gray-100" {...props} />
        ),
        th: ({ node, ...props }) => (
          <th className="border border-gray-300 px-3 py-1.5 text-left font-semibold text-gray-900" {...props} />
        ),
        td: ({ node, ...props }) => (
          <td className="border border-gray-300 px-3 py-1.5 text-gray-800" {...props} />
        ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownContent;
